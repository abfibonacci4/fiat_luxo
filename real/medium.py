
import asyncio
import math

import techmanpy


ROBOT_IP = "172.16.8.2"

HOME = [-259.13, -89.25, 573.31, -163.75, 17.14, 145.85]
LOOK = [-256.15, -86.56, 433.84, -152.37, 14.73, 149.03]
ARC_VIA_1 = [-223.56, -48.63, 540.83, -164.02, 25.71, 142.07]
END_1 = [-381.88, -179.05, 482.17, 178.89, 28.07, 134.32]

LOOK_SPEED = 0.5
APPROACH_SPEED = 0.5
ARC_1_SPEED = 0.3
RETURN_SPEED = 0.5

ACCELERATION_MS = 500
RETURN_ACCELERATION_MS = 500
LOOK_ACCELERATION_MS = 500
ARC_ACCELERATION_MS = 800

PAUSE_SECONDS = 2.5


def validate_pose(pose: list[float]) -> None:
    if len(pose) != 6 or not all(math.isfinite(x) for x in pose):
        raise ValueError("Pose must contain six finite values.")


async def wait_for_motion(robot, tag: int) -> None:
    await robot.set_queue_tag(tag, wait_for_completion=True)


async def main() -> None:
    for pose in (HOME, LOOK, ARC_VIA_1, END_1):
        validate_pose(pose)

    print("Motion: HOME -> LOOK -> ARC_VIA_1 -> END_1")

    confirmation = input(
        "Type MOVE after validating the complete trajectory: "
    )

    if confirmation != "MOVE":
        print("Motion cancelled.")
        return

    async with techmanpy.connect_sct(robot_ip=ROBOT_IP) as robot:
        # 1. Move to HOME.
        print("Moving to HOME...")
        await robot.move_to_point_ptp(
            tcp_point_goal=HOME,
            speed_perc=RETURN_SPEED,
            acceleration_duration=RETURN_ACCELERATION_MS,
            blending_perc=0.0,
        )
        await wait_for_motion(robot, tag=1)

        # 2. Move straight from HOME to LOOK.
        print("Moving straight to LOOK...")
        await robot.move_to_point_line(
            tcp_point_goal=LOOK,
            speed=APPROACH_SPEED,
            acceleration_duration=ACCELERATION_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=2)

        # 3. Pause at LOOK.
        print(f"Pausing for {PAUSE_SECONDS} seconds...")
        await asyncio.sleep(PAUSE_SECONDS)

        # 4. Arc from LOOK, through ARC_VIA_1, to END_1.
        print("Moving along arc to END_1...")
        await robot.move_on_circle(
            tcp_point_1=ARC_VIA_1,
            tcp_point_2=END_1,
            speed=ARC_1_SPEED,
            acceleration_duration=ARC_ACCELERATION_MS,
            arc_angle=0,
            blending_perc=0.0,
        )
        await wait_for_motion(robot, tag=3)

        print("Motion completed at END_1.")


if __name__ == "__main__":
    asyncio.run(main())
