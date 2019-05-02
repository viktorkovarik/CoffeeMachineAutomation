#include "esphome.h"
using namespace esphome;

class WaterLED : public PollingComponent, public binary_sensor::BinarySensor {
 public:
    // constructor
    WaterLED() : PollingComponent(1500) {}
    int cnt_filtering_val = 10;
    int filtering_indexWATER = cnt_filtering_val;
    int oncePrintWaterErr = 0;
    int water = 0;

    int filter(int *index, int act_val){
        if(act_val){
            if(*index != 0){
                *index -= 1;
                if(*index <= 0) *index = 0;
                    return 0;
            }
            else return 1;
        }   
        else if(!act_val){
            *index = cnt_filtering_val;
            return 0;
        }  
    }

    void setup() override {
        // This will be called by App.setup()
        pinMode(3, INPUT);
        publish_state(0);
    }
    void update() override {
        // This will be called every "update_interval" milliseconds.

        // Publish an OFF state
        int val = filter(&filtering_indexWATER, digitalRead(3));  

        if (val == 1){
            if(oncePrintWaterErr == 0){
                water = 0; // FAIL 1
                publish_state(val);
                oncePrintWaterErr = 1;
            }
        }
        else{
            if(oncePrintWaterErr == 1){
                water = 1; // OK 0
                publish_state(val);
                oncePrintWaterErr = 0;
            }
        }
        
    }
};