from sensor_library import *
from gpiozero import *
import time
import sys

DistanceSensor = Distance_Sensor()
vibrationMotor = LED(26)
buzzer = Buzzer(27)
vibrationMotor.off()
switch = Button(10)
power = Button(17)

        
def stimulate(): ## shows whether the device is on or off
    if power.is_pressed:
        status = 1
    else:
        status = 0
    return status

def mode_setting(): ## shows the current process that the device is running, Walk or Reach
    if switch.is_pressed:
        status = 'Walk'
    else:
        status = 'Reach'

    return status

def raw_data(DistanceSensor, dist_list): # returns a list with all the recorded distances, last one newest 
    dist = DistanceSensor.distance()

    if dist < 8190:
        dist_list.append(dist)

    return dist_list

def rolling_avg(dist_list): # creates a rolling average using the 5 latest data points of raw distance data, but alternating

    if len(dist_list) >= 5:
        avg = round((dist_list[-1]+dist_list[-3]+dist_list[-5])/3, 1)
    else:
        avg = None
    return avg

def init_file(): # creates a data file to append data on mode and distances in
    with open("data_file.txt", 'w') as file:
        file.write('Raw Data'+'\t'+'Average Data'+'\t'+'Device Mode \n')

def append_file(DistanceSensor, dist_list): # appends an instance of raw data, rolling avg, and mode of device to data file
    dist_list = raw_data(DistanceSensor, dist_list)
    avg = rolling_avg(dist_list)
    mode = mode_setting()
    
    #adds the data to the next line, adds newline
    with open("data_file.txt", 'a') as file:
        file.write(str(round(dist_list[-1], 2)) + '\t\t' + str(avg) + '\t\t' + mode + '\n')    

def walk_timing(avg): # Defines the timing interval for frequency of vibration for Walk mode
    if avg != None:
        if avg >= 250:
            x = (avg)/(1800)
        else:
            x = 0.001
        return x
        
    else:
        return 0

def reach_timing(avg): # Defines the timing interval for frequency of vibration for Reach mode
    if avg != None:
        if avg <= 450 and avg >= 300:
            x = 0.5
        elif avg < 300 and avg > 150:
            x = 0.2
        elif avg >= 150:
            x = 0.1
        else:
            x = 0.001

        return x
    else:
        return 0


def init_shell(): # Initializes the shell for the viewer to understand the proceeding data
    print('Power Status' + '\t' + 'Device Mode' + '\t' + 'Distance' + '\t' + 'Rolling Avg' + '\t' + 'Vibration Interval (s)')

def format_shell(power_status, mode, distance, roll_avg, vibe_interval): # Displays respective information on the Python Shell
    if power_status == 1:
        power = 'ON'
    elif power_status == 0:
        power = 'OFF'
    print(power + '\t\t' + mode + '\t\t' + str(distance) + '\t\t' + str(roll_avg) + '\t\t' + str(round(vibe_interval, 1)))

def main(): # The implementation of code
    distlist = []
    init_file()

    while True: # The process is started
        power = stimulate()
        
        if power == 1: # Announces activation of device
            buzzer.on()
            print('Buzzer is ON')
            time.sleep(0.5)
            buzzer.off()
            print('Buzzer is OFF')

        if power == 1: 
            init_shell()
        
        while (mode_setting() == 'Walk') and (power == 1): ## WALK MODE
            distlist = raw_data(DistanceSensor, distlist)
            aveg = rolling_avg(distlist)
            y = walk_timing(aveg)
            format_shell(stimulate(), mode_setting(), DistanceSensor.distance(), aveg, y)
            start = time.time()

            while (y == 0.001) and (power == 1): # When the distance is very little, this while loop makes the vibrator continuously vibrate
                vibrationMotor.on()
                distlist = raw_data(DistanceSensor, distlist)
                aveg = rolling_avg(distlist)
                y = walk_timing(aveg)
                format_shell(stimulate(), mode_setting(), DistanceSensor.distance(), aveg, y)
                
                append_file(DistanceSensor, distlist) # All append_file calls are to add the previously determined average distance (by raw_data calls) into the file 

                if y != 0.001: # If distance is very small, the while loop breaks
                    start = time.time()
                    break

                if power == 0:
                    break 


            while ((time.time() - start) <= 0.1 and DistanceSensor.distance() <= 3000) and (y != 0.001) and (power == 1): # This establishes the interval where the vibrator will be on as long as the power is on and the distance is within 3000mm
                vibrationMotor.on()
                format_shell(stimulate(), mode_setting(), DistanceSensor.distance(), aveg, y)
                distlist = raw_data(DistanceSensor, distlist)
                append_file(DistanceSensor, distlist)

                power = stimulate()
                if power == 0:
                    break
                
            start2 = time.time()
            while ((time.time() - start2) <= y or DistanceSensor.distance() > 3000) and power == 1: # This establishes the interval where the vibrator will be off to create a pattern, or when it will be off if the distance is greater than 3000mm
                vibrationMotor.off()
                format_shell(stimulate(), mode_setting(), DistanceSensor.distance(), aveg, y)
                distlist = raw_data(DistanceSensor, distlist)
                append_file(DistanceSensor, distlist)

                power = stimulate()
                if power == 0:
                    break
            distlist = raw_data(DistanceSensor, distlist)
            append_file(DistanceSensor, distlist)

            power = stimulate()
            if power == 0: # All if statements where power == 1 break out of the loop and end the program
                vibrationMotor.off()
                break
            
        if power == 1: # When walk mode is switched out of and the power is still on, two beeps announce the beginning of reach mode
            buzzer.on()
            print('Buzzer is ON')
            time.sleep(0.5)
            buzzer.off()
            print('Buzzer is OFF')
            time.sleep(0.5)
            buzzer.on()
            print('Buzzer is ON')
            time.sleep(0.5)
            buzzer.off()
            print('Buzzer is OFF')
            

        if power == 1:
            init_shell()
        
        while (mode_setting() == 'Reach') and (power == 1): ## REACH MODE 
            distlist = raw_data(DistanceSensor, distlist)
            aveg = rolling_avg(distlist)
            y = reach_timing(aveg)

            format_shell(stimulate(), mode_setting(), DistanceSensor.distance(), aveg, y)

            start = time.time()

            while (y == 0.001) and (power == 1): # When the distance is very little, this while loop makes the vibrator continuously vibrate
                vibrationMotor.on()
                distlist = raw_data(DistanceSensor, distlist)
                aveg = rolling_avg(distlist)
                y = reach_timing(aveg)
                format_shell(stimulate(), mode_setting(), DistanceSensor.distance(), aveg, y)
                
                append_file(DistanceSensor, distlist)

                if y != 0.001: # If distance is very small, the while loop breaks
                    start = time.time()
                    break

                if power == 0:
                    break 

            while ((time.time() - start) <= 0.1 and DistanceSensor.distance() <= 450) and (y != 0.001) and (power == 1): # This establishes the interval where the vibrator will be on as long as the power is on and the distance is within 450mm
                vibrationMotor.on()
                format_shell(stimulate(), mode_setting(), DistanceSensor.distance(), aveg, y)
                distlist = raw_data(DistanceSensor, distlist)
                append_file(DistanceSensor, distlist)

                power = stimulate()
                if power == 0:
                    break

            start2 = time.time()
            while ((time.time() - start2) <= y or DistanceSensor.distance() > 450) and (power == 1): # This establishes the interval where the vibrator will be off to create a pattern, or when it will be off if the distance is greater than 450mm
                vibrationMotor.off()
                format_shell(stimulate(), mode_setting(), DistanceSensor.distance(), aveg, y)
                distlist = raw_data(DistanceSensor, distlist)
                append_file(DistanceSensor, distlist)

                power = stimulate()
                if power == 0:
                    break

            distlist = raw_data(DistanceSensor, distlist)
            append_file(DistanceSensor, distlist)

            power = stimulate()
            if power == 0:
                vibrationMotor.off()
                break

    vibrationMotor.off() # When all loops are broken out of, the vibrator and buzzer are turned off
    buzzer.off()

main()