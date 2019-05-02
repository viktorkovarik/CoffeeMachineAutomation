/*
 * ESPhome RC522 RFID plugin with access control
 * 
 * Created on: 17.03.2019
 *
 * Copyright (c) 2019 Jakub Pachciarek. All rights reserved.
 * 
 * EDITED BY xkovar77
 * 
 */

#include "esphome.h"
#include <SPI.h>
#include <MFRC522.h>

using namespace esphome;
using namespace std;

class RfidSensorsComponent : public Component {
 private:
  MFRC522 rfid;

  typedef struct {
      String id;
      String description;
  } user;

  vector<user> users_list;

  unsigned long last_tag_read_milis = 0;

  void convertCardByte(byte *uidByte, unsigned int *card) {
    *card =  uidByte[0] << 24;
    *card += uidByte[1] << 16;
    *card += uidByte[2] <<  8;
    *card += uidByte[3];
    return;
  }

  void handle_tag_read() {
    if (last_tag_read_milis != 0 && (last_tag_read_milis + 5000) > millis()) return;

    if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

    user current_tag;
    bool known_tag = false;

    char tag_id_buffer[12];
    sprintf(tag_id_buffer, "%02X:%02X:%02X:%02X", rfid.uid.uidByte[0], rfid.uid.uidByte[1], rfid.uid.uidByte[2], rfid.uid.uidByte[3]);
    current_tag.id = tag_id_buffer;

    unsigned int NFC_id;

    convertCardByte(rfid.uid.uidByte,&NFC_id);

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    for (size_t i = 0; i < users_list.size(); i++) {
      if (users_list[i].id == current_tag.id) {
        current_tag = users_list[i];
        known_tag = true;
        break;
      }
    }

    ESP_LOGD("rfid", "Tag with id %s found!", current_tag.id.c_str());
    ESP_LOGD("rfid", "Setting sensor states...");

    last_tag_read_milis = millis();

    state->publish_state(NFC_id);
    
  }

 public:
  sensor::Sensor *state = new sensor::Sensor();

  void setup() override {
    SPI.begin();
    rfid.PCD_Init(15, 1);
  }

  void loop() override {
    handle_tag_read();
  }
};