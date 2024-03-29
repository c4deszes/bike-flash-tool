#include "line_protocol.h"
#include "flash_line_diag.h"
#include "flash_line_api.h"

LINE_Diag_SoftwareVersion_t sw_version = {
  .major = 0,
  .minor = 1,
  .patch = 0,
  .reserved = 0
};

LINE_Diag_PowerStatus_t power_status = {
  .U_status = LINE_DIAG_POWER_STATUS_VOLTAGE_OK,
  .BOD_status = LINE_DIAG_POWER_STATUS_BOD_NONE,
  .I_operating = LINE_DIAG_POWER_STATUS_OP_CURRENT(100),  // 100mA
  .I_sleep = LINE_DIAG_POWER_STATUS_SLEEP_CURRENT(20)    // 20uA
};

uint8_t LINE_Diag_GetOperationStatus(void) {
  return LINE_DIAG_OP_STATUS_BOOT;
}

LINE_Diag_PowerStatus_t* LINE_Diag_GetPowerStatus(void) {
  return &power_status;
}

uint32_t LINE_Diag_GetSerialNumber(void) {
  return 0xDEADBEEF;
}

LINE_Diag_SoftwareVersion_t* LINE_Diag_GetSoftwareVersion(void) {
  return &sw_version;
}

void LINE_Diag_OnWakeup(void) {
  Serial.println("Waking up.");
}

void LINE_Diag_OnSleep(void) {
  Serial.println("Going to sleep.");
}

void LINE_Diag_OnShutdown(void) {
  Serial.println("Shutting down.");
}

void LINE_Diag_OnConditionalChangeAddress(uint8_t old_address, uint8_t new_address) {
    Serial.println("Changed address: ");
    Serial.print(old_address, HEX);
    Serial.print(" -> ");
    Serial.print(new_address, HEX);
    Serial.println();
}

uint8_t FLASH_BL_EnterBoot(void) {
    Serial.println("Entering bootloader.");
    return FLASH_LINE_BOOT_ENTRY_SUCCESS;
}

fl_BootSignature_t* FLASH_BL_ReadSignature(void);

void FLASH_BL_OnPageWrite(uint32_t address, uint8_t size, uint8_t* data) {
  Serial.println("Writing page.");
}

uint8_t FLASH_BL_GetWriteStatus(void) {
  return FLASH_LINE_PAGE_WRITE_SUCCESS;
}

void FLASH_BL_ExitBoot(void) {
  Serial.println("Exiting boot.");
}

void LINE_Transport_OnError(bool response, uint16_t request, line_transport_error error_type) {
  if (error_type == line_transport_error_timeout) {
    Serial.println("Timeout.");
  }
  else if (error_type == line_transport_error_header_invalid) {
    Serial.println("Header error.");
  }
  else if (error_type == line_transport_error_data_invalid) {
    Serial.println("Checksum error.");
  }
  else {
    Serial.println("Unknown error.");
  }
}

void LINE_Transport_WriteResponse(uint8_t size, uint8_t* payload, uint8_t checksum) {
  Serial1.write(size);
  for (int i=0;i<size;i++) {
    Serial1.write(payload[i]);
  }
  Serial1.write(checksum);
  Serial1.flush();
  Serial.println("Sent response.");
}

void setup() {
  Serial.begin(9600);
  while(!Serial);

  Serial1.begin(19200);

  LINE_Transport_Init(true);
  LINE_App_Init();
  //LINE_Diag_SetAddress(0x5);
  FLASH_LINE_Init(FLASH_LINE_BOOTLOADER_MODE);

  pinMode(8, OUTPUT);
  Serial.println("Initialized.");
}

uint32_t transport_timer = 0;

void loop() {
  while(Serial1.available() > 0) {
    uint8_t data = Serial1.read();
    Serial.print("Received: ");
    Serial.print(data, HEX);
    Serial.println();
    LINE_Transport_Receive(data);
  }
  uint32_t currentTime = millis();
  uint32_t diff = currentTime - transport_timer;
  if (diff >= 1) {
    LINE_Transport_Update(diff);
    transport_timer = currentTime;
  }

}
