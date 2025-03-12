
#https://github.com/SERLatBTH/StarterGuide-Dobot-Magician-with-Python
import DobotDllType as dType
import time

api = dType.load()

dType.ConnectDobot(api, "COM3", 115200)[0]  # Change COM port if necessary

class Movement:
    @staticmethod
    def get_current_pos():
        return dType.GetPose(api)

    @staticmethod
    def move_to_location(x, y, z, r=0):
        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x, y, z, r, 1)
        time.sleep(1)

    @staticmethod
    def move_down(z):
        current_pos = Movement.get_current_pos()
        Movement.move_to_location(current_pos[0], current_pos[1], z)
    
    @staticmethod
    def move_up(z):
        current_pos = Movement.get_current_pos()
        Movement.move_to_location(current_pos[0], current_pos[1], z)

    @staticmethod
    def suction_cup_toggle(state):
        dType.SetEndEffectorSuctionCup(api, 1, state)
        time.sleep(0.5)

    @staticmethod
    def move_away():
        Movement.move_to_location(200, 0, 150)  # Move to a safe position

if __name__ == "__main__":
    # Example sequence to pick and place a card
    Movement.move_to_location(150, 50, 50)  # Move above the card
    Movement.move_down(10)  # Lower to pick up
    Movement.suction_cup_toggle(1)  # Turn suction on
    Movement.move_up(100)  # Lift the card
    Movement.move_to_location(200, -50, 50)  # Move to the new position
    Movement.move_down(10)  # Lower to drop
    Movement.suction_cup_toggle(0)  # Turn suction off
    Movement.move_away()  # Move back to safe position
