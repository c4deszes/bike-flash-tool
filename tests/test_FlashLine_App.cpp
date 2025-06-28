#include "gtest/gtest.h"
#include "fff.h"

extern "C" {
    #include "flash_line_diag.h"
    #include "flash_line_api.h"

    #include "line_protocol.h"
    #include "line_tester.h"
}

DEFINE_FFF_GLOBALS;

FAKE_VALUE_FUNC0(fl_BootEntryResponse_t, FLASH_BL_EnterBoot);

// Diagnostic callbacks
FAKE_VALUE_FUNC0(uint32_t, LINE_Diag_GetSerialNumber);
FAKE_VALUE_FUNC0(LINE_Diag_SoftwareVersion_t*, LINE_Diag_GetSoftwareVersion);
FAKE_VALUE_FUNC0(LINE_Diag_PowerStatus_t*, LINE_Diag_GetPowerStatus);
FAKE_VALUE_FUNC0(uint8_t, LINE_Diag_GetOperationStatus);

// Transport callbacks
FAKE_VOID_FUNC4(LINE_Transport_OnError, uint8_t, bool, uint16_t, line_transport_error);
FAKE_VOID_FUNC4(LINE_Transport_WriteResponse, uint8_t, uint8_t, uint8_t*, uint8_t);
FAKE_VOID_FUNC2(LINE_Transport_WriteRequest, uint8_t, uint16_t);

// Adapters to enable diagnostics over the transport layer
bool LINE_Transport_RespondsTo(uint8_t channel, uint16_t request) {
    return LINE_Diag_RespondsTo(channel, request);
}

bool LINE_Transport_PrepareResponse(uint8_t channel, uint16_t request, uint8_t* size, uint8_t* payload) {
    return LINE_Diag_PrepareResponse(channel, request, size, payload);
}

void LINE_Transport_OnData(uint8_t channel, bool response, uint16_t request, uint8_t size, uint8_t* payload) {
    if (!response) {
        LINE_Diag_OnRequest(channel, request, size, payload);
    }
}

#define UINT16_L(x) ((uint8_t)(x & 0xFF))
#define UINT16_H(x) ((uint8_t)((x >> 8) & 0xFF))

#define TEST_NODE_ADDRESS 0x5

LINE_Diag_Config_t diag_config = {
    .transport_channel = 0,
    .address = TEST_NODE_ADDRESS,
    .op_status = LINE_Diag_GetOperationStatus,
    .power_status = LINE_Diag_GetPowerStatus,
    .serial_number = LINE_Diag_GetSerialNumber,
    .software_version = LINE_Diag_GetSoftwareVersion
};

class TestFlashLineApplicationMode : public testing::Test {
public:
    static void SetUpTestSuite() {
        LINE_Transport_Init(0, false);
        LINE_Diag_Init(0, &diag_config);
        FLASH_LINE_Init(0, FLASH_LINE_APPLICATION_MODE);

        LINE_Diag_GetSerialNumber_fake.return_val = 0x12345678;
    }
protected:
    void SetUp() override {
        
    }
};

TEST_F(TestFlashLineApplicationMode, BootEntrySuccess) {
    FLASH_BL_EnterBoot_fake.return_val = {FLASH_LINE_BOOT_ENTRY_SUCCESS, 0x12345678};

    BUILD_REQUEST(response, FLASH_LINE_DIAG_BOOT_ENTRY | TEST_NODE_ADDRESS);
    for (int i = 0; i < sizeof(response); i++) {
        LINE_Transport_Receive(0, response[i]);
    }

    EXPECT_EQ(FLASH_BL_EnterBoot_fake.call_count, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val, 4);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg2_val[0], 0x78);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg2_val[1], 0x56);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg2_val[2], 0x34);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg2_val[3], 0x12);
}

// TODO: this doesn't need to be tested here
TEST_F(TestFlashLineApplicationMode, BootEntryNotTargeted) {
    FLASH_BL_EnterBoot_fake.return_val = {FLASH_LINE_BOOT_ENTRY_SUCCESS, 0x12345678};

    BUILD_REQUEST(response, FLASH_LINE_DIAG_BOOT_ENTRY | (TEST_NODE_ADDRESS + 1));
    for (int i = 0; i < sizeof(response); i++) {
        LINE_Transport_Receive(0, response[i]);
    }

    EXPECT_EQ(FLASH_BL_EnterBoot_fake.call_count, 0);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.call_count, 0);
}

TEST_F(TestFlashLineApplicationMode, BootEntryFailure) {
    FLASH_BL_EnterBoot_fake.return_val = {FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT, 0x12345678};

    BUILD_REQUEST(response, FLASH_LINE_DIAG_BOOT_ENTRY | TEST_NODE_ADDRESS);
    for (int i = 0; i < sizeof(response); i++) {
        LINE_Transport_Receive(0, response[i]);
    }

    EXPECT_EQ(FLASH_BL_EnterBoot_fake.call_count, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val, 1);
    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg2_val[0], FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT);
}

TEST_F(TestFlashLineApplicationMode, ReadSignatureNoResponse) {
    BUILD_REQUEST(response, FLASH_LINE_DIAG_READ_SIGNATURE | TEST_NODE_ADDRESS);
    for (int i = 0; i < sizeof(response); i++) {
        LINE_Transport_Receive(0, response[i]);
    }

    EXPECT_EQ(LINE_Transport_WriteResponse_fake.arg1_val, 0);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
