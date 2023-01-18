import math


def center_camera(spectator, ped, rot_offset=0):
    # Rotate the camera to face the pedestrian and apply an offset
    trans = ped.get_transform()
    offset_radians = 2 * math.pi * rot_offset / 360
    x = math.cos(offset_radians) * -2
    y = math.sin(offset_radians) * 2
    trans.location.x += x
    trans.location.y += y
    trans.location.z = 2
    trans.rotation.pitch = -16
    trans.rotation.roll = 0
    trans.rotation.yaw = -rot_offset
    spectator.set_transform(trans)
    return trans