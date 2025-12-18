import time
import json
import threading

class LoggingScheduler:
    # Constructor for LoggingScheduler class
    def __init__(self, mqtt_client, shared_log):
        # Store MQTT client created in pi_controller.py
        self.client = mqtt_client
        self.shared_log = shared_log
        # Store the 'next run time' for each system
        self.next_primary = {}  # { 'system_1': timestamp }
        self.next_sampling = {} 
        self.running = True # flag check to esnure pi finishes its process before thread dies

    def start(self):
        """Starts the timer loop in a background thread."""
        # Execute _loop function, kill thread automatically if main program stops
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        while self.running:
            now = time.time()  # grabs the current Unix timestamp
                 
            for system_id, config in self.shared_log.items():
                # 3600 and 43200 are fallback defaults
                p_interval = config.get('primary_log_interval', 3600)
                s_interval = config.get('sampling_log_interval', 43200)

                # --- Handle Primary Sensors ---
                # Pi doesn't have a schedule for system_X yet
                if system_id not in self.next_primary:
                    self.next_primary[system_id] = now + p_interval
                
                # Check if current time past the scheduled logging time
                if now >= self.next_primary[system_id]:
                    self._trigger_log(system_id, "GET_PRIMARY")
                    # Reset the clock
                    self.next_primary[system_id] = now + p_interval

                # --- Handle Sampling Sensors ---
                if system_id not in self.next_sampling:
                    self.next_sampling[system_id] = now + s_interval
                
                if now >= self.next_sampling[system_id]:
                    self._trigger_log(system_id, "GET_SAMPLING")
                    self.next_sampling[system_id] = now + s_interval

            time.sleep(1) # Check every second

    def _trigger_log(self, system_id, log_type):
        topic = f"{system_id}/log_sensor"
        payload = {"type": log_type}
        self.client.publish(topic, json.dumps(payload), qos=1)
        print(f"Timer reached for {system_id}: Sent {log_type} to {topic}")

    def stop(self):
        self.running = False