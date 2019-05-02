#include "esphome.h"
using namespace esphome;

class BusyState : public PollingComponent, public binary_sensor::BinarySensor {
 public:
    // constructor
    BusyState() : PollingComponent(300) {}

    int indexGreenLED = 0;
    int indexBusyState = 0;

    int filterbusyState(int *val){    
        int act_val = *val;
        
        if(act_val){
            indexBusyState++;
            if(indexBusyState > 60){
                indexBusyState = 60;
                return 0; // not busy
            }
        }
        else if(!act_val){
            indexBusyState = 0;
            return 1; // busy
        };
        return 1;
    }
    int filterGreenLed(int *val){    
        int act_val = *val;
        // nsviti sviti led => act_val = 0
        if(!act_val){
            indexGreenLED++;
            if(indexGreenLED > 10){
                indexGreenLED = 10;
                return 1; // off nesviti
            }
        }
        else if(act_val){
            indexGreenLED = 0;
            return 0; // on sviti
        };
        return 0;
    }

    void setup() override {
        // This will be called by App.setup()
        pinMode(A0, INPUT);
        publish_state(1);
    }
    void update() override {
        // This will be called every "update_interval" milliseconds.

        // Publish an OFF state
        int state = analogRead(A0);
        int diodeLight = !filterGreenLed(&state); // 1- sviti 0-nesviti

        int tmp = filterbusyState(&diodeLight);

        publish_state(!tmp);
    }
};