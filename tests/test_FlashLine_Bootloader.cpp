#include "gtest/gtest.h"
#include "fff.h"

extern "C" {
    #include "flash_line_diag.h"
    #include "flash_line_api.h"

    #include "line_protocol.h"
}

DEFINE_FFF_GLOBALS;

FAKE_VALUE_FUNC0(fl_BootSignature_t*, FLASH_BL_ReadSignature);
FAKE_VOID_FUNC3(FLASH_BL_OnPageWrite, uint32_t, uint8_t, uint8_t*);
FAKE_VALUE_FUNC0(uint8_t, FLASH_BL_GetWriteStatus);

FAKE_VALUE_FUNC0(uint32_t, LINE_Diag_GetSerialNumber);
FAKE_VALUE_FUNC0(LINE_Diag_SoftwareVersion_t*, LINE_Diag_GetSoftwareVersion);
FAKE_VALUE_FUNC0(LINE_Diag_PowerStatus_t*, LINE_Diag_GetPowerStatus);
FAKE_VALUE_FUNC0(uint8_t, LINE_Diag_GetOperationStatus);

// Transport callbacks
FAKE_VOID_FUNC3(LINE_Transport_OnError, bool, uint16_t, line_transport_error);
FAKE_VOID_FUNC3(LINE_Transport_WriteResponse, uint8_t, uint8_t*, uint8_t);

class TestFlashLineBootloaderMode : public testing::Test {
public:
    static void SetUpTestSuite() {
        LINE_Transport_Init(false);
        LINE_Diag_Init();
        LINE_Diag_SetAddress(0x5);
        FLASH_LINE_Init(FLASH_LINE_BOOTLOADER_MODE);

        LINE_Diag_GetSerialNumber_fake.return_val = 0x12345678;
    }
protected:
    void SetUp() override {
        
    }
};

TEST_F(TestFlashLineBootloaderMode, ReadSignatureNull) {
    FLASH_BL_ReadSignature_fake.return_val = NULL;

    uint8_t data[] = {0x55, 0x8E, 0x65};
    for (int i = 0; i < sizeof(data); i++) {
        LINE_Transport_Receive(data[i]);
    }

    EXPECT_EQ(FLASH_BL_ReadSignature_fake.call_count, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.call_count, 0);
}

TEST_F(TestFlashLineBootloaderMode, ReadSignatureValid) {
    // TODO: signature value
    fl_BootSignature_t signature = {
        .mcu_identifier = "ATSAMD21E18A",
        .mcu_revision = (uint16_t)'A'
    };
    FLASH_BL_ReadSignature_fake.return_val = &signature;

    uint8_t data[] = {0x55, 0x8E, 0x65};
    for (int i = 0; i < sizeof(data); i++) {
        LINE_Transport_Receive(data[i]);
    }

    EXPECT_EQ(FLASH_BL_ReadSignature_fake.call_count, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.call_count, 1);
    //TODO: validate response content
}

TEST_F(TestFlashLineBootloaderMode, PageWrite) {
    uint8_t data[] = {0x55, 0x4E, 0x85, 4 + 16,
                      0x78, 0x56, 0x34, 0x12,
                      0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                      0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
                      0x43};
    for (int i = 0; i < sizeof(data); i++) {
        LINE_Transport_Receive(data[i]);
    }

    EXPECT_EQ(FLASH_BL_OnPageWrite_fake.call_count, 1);
    EXPECT_EQ(FLASH_BL_OnPageWrite_fake.arg0_val, 0x12345678);
    for (int i = 0; i < 16; i++) {
        EXPECT_EQ(FLASH_BL_OnPageWrite_fake.arg2_val[i], i);
    }
}

TEST_F(TestFlashLineBootloaderMode, GetWriteStatus) {
    FLASH_BL_GetWriteStatus_fake.return_val = FLASH_LINE_PAGE_NOT_WRITTEN;

    uint8_t data[] = {0x55, 0xCE, 0xA5};
    for (int i = 0; i < sizeof(data); i++) {
        LINE_Transport_Receive(data[i]);
    }

    EXPECT_EQ(FLASH_BL_GetWriteStatus_fake.call_count, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg0_val, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val[0], FLASH_LINE_PAGE_NOT_WRITTEN);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
