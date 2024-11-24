#include "gtest/gtest.h"
#include "fff.h"

extern "C" {
    #include "flash_line_diag.h"
    #include "flash_line_api.h"

    #include "line_protocol.h"
}

DEFINE_FFF_GLOBALS;

FAKE_VALUE_FUNC0(uint8_t, FLASH_BL_EnterBoot);
FAKE_VALUE_FUNC0(uint32_t, LINE_Diag_GetSerialNumber);
FAKE_VALUE_FUNC0(LINE_Diag_SoftwareVersion_t*, LINE_Diag_GetSoftwareVersion);
FAKE_VALUE_FUNC0(LINE_Diag_PowerStatus_t*, LINE_Diag_GetPowerStatus);
FAKE_VALUE_FUNC0(uint8_t, LINE_Diag_GetOperationStatus);

// Transport callbacks
FAKE_VOID_FUNC3(LINE_Transport_OnError, bool, uint16_t, line_transport_error);
FAKE_VOID_FUNC3(LINE_Transport_WriteResponse, uint8_t, uint8_t*, uint8_t);
FAKE_VOID_FUNC1(LINE_Transport_WriteRequest, uint16_t);

class TestFlashLineApplicationMode : public testing::Test {
public:
    static void SetUpTestSuite() {
        LINE_Transport_Init(false);
        LINE_Diag_Init();
        LINE_Diag_SetAddress(0x5);
        FLASH_LINE_Init(FLASH_LINE_APPLICATION_MODE);

        LINE_Diag_GetSerialNumber_fake.return_val = 0x12345678;
    }
protected:
    void SetUp() override {
        
    }
};

TEST_F(TestFlashLineApplicationMode, BootEntrySuccess) {
    FLASH_BL_EnterBoot_fake.return_val = FLASH_LINE_BOOT_ENTRY_SUCCESS;

    uint8_t data[] = {0x55, 0x0E, 0x45};

    for (int i = 0; i < sizeof(data); i++) {
        LINE_Transport_Receive(data[i]);
    }

    EXPECT_EQ(FLASH_BL_EnterBoot_fake.call_count, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg0_val, 4);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val[0], 0x78);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val[1], 0x56);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val[2], 0x34);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val[3], 0x12);
}

TEST_F(TestFlashLineApplicationMode, BootEntryNotTargeted) {
    FLASH_BL_EnterBoot_fake.return_val = FLASH_LINE_BOOT_ENTRY_SUCCESS;

    uint8_t data[] = {0x55, 0x4E, 0x46};

    for (int i = 0; i < sizeof(data); i++) {
        LINE_Transport_Receive(data[i]);
    }

    EXPECT_EQ(FLASH_BL_EnterBoot_fake.call_count, 0);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.call_count, 0);
}

TEST_F(TestFlashLineApplicationMode, BootEntryFailure) {
    FLASH_BL_EnterBoot_fake.return_val = FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT;

    uint8_t data[] = {0x55, 0x0E, 0x45};

    for (int i = 0; i < sizeof(data); i++) {
        LINE_Transport_Receive(data[i]);
    }

    EXPECT_EQ(FLASH_BL_EnterBoot_fake.call_count, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg0_val, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val[0], FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT);
}

TEST_F(TestFlashLineApplicationMode, ReadSignatureNoResponse) {
    uint8_t data[] = {0x55, 0x8E, 0x65};

    for (int i = 0; i < sizeof(data); i++) {
        LINE_Transport_Receive(data[i]);
    }

    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg0_val, 0);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
