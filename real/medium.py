
import asyncio
import math

import techmanpy


ROBOT_IP = "172.16.8.2"

HOME = [-259.13, -89.25, 573.31, -163.75, 17.14, 145.85]
LOOK = [-256.15, -86.56, 433.84, -152.37, 14.73, 149.03]
ARC_VIA_1 = [-223.56, -48.63, 540.83, -164.02, 25.71, 142.07]
END_1 = [-381.88, -179.05, 482.17, 178.89, 28.07, 134.32]
ARC_VIA_2 = [-211.51, -228.71, 651.08, -174.27, -14.38, -177.95]
END_2 = [-207.17, -452.93, 472.26, 142.17, -16.00, -156.25]
PARTICIPANT = [-135.53, -206.33, 542.94, -96.30, -4.28, -162.58]
HEAD_TILT = [-122.31, -207.99, 552.19, -104.34, -28.53, -147.80]


LOOK_SPEED = 0.7
APPROACH_SPEED = 0.5
ARC_1_SPEED = 0.5
ARC_2_SPEED = 0.5
RETURN_SPEED = 0.5
RETURN_SPEED_SLOW = 0.3


ACCELERATION_MS = 500
RETURN_ACCELERATION_MS = 500
RETURN_ACCELERATION_SLOW_MS = 800
LOOK_ACCELERATION_MS = 500
ARC_ACCELERATION_MS = 800

PAUSE_SECONDS = 2.0
END_PAUSE_SECONDS = 1.0
HEAD_TILT_PAUSE_SECONDS = 0.5


def validate_pose(pose: list[float]) -> None:
    if len(pose) != 6 or not all(math.isfinite(x) for x in pose):
        raise ValueError("Pose must contain six finite values.")


async def wait_for_motion(robot, tag: int) -> None:
    await robot.set_queue_tag(tag, wait_for_completion=True)


async def main() -> None:
    for pose in (
        HOME,
        LOOK,
        ARC_VIA_1,
        END_1,
        ARC_VIA_2,
        END_2,
        PARTICIPANT,
        HEAD_TILT,
    ):
        validate_pose(pose)

    print(
        "Motion: HOME -> LOOK -> ARC_VIA_1 -> END_1 "
        "-> ARC_VIA_1 -> LOOK -> HOME -> ARC_VIA_2 "
        "-> END_2 -> ARC_VIA_2 -> LOOK -> PARTICIPANT "
        "-> HEAD_TILT -> PARTICIPANT -> HOME"
    )

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

        # 4. Arc from LOOK through ARC_VIA_1 to END_1.
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

        print(f"Pausing at END_1 for {END_PAUSE_SECONDS} second...")
        await asyncio.sleep(END_PAUSE_SECONDS)

        # 5. Reverse the arc from END_1 through ARC_VIA_1 to LOOK.
        print("Returning along arc to LOOK...")
        await robot.move_on_circle(
            tcp_point_1=ARC_VIA_1,
            tcp_point_2=LOOK,
            speed=ARC_1_SPEED,
            acceleration_duration=ARC_ACCELERATION_MS,
            arc_angle=0,
            blending_perc=0.0,
        )
        await wait_for_motion(robot, tag=4)

        # 6. Move straight from LOOK back to HOME.
        print("Moving straight back to HOME...")
        await robot.move_to_point_line(
            tcp_point_goal=HOME,
            speed=RETURN_SPEED,
            acceleration_duration=RETURN_ACCELERATION_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=5)

        # # 7. Arc from HOME through ARC_VIA_2 to END_2.
        # print("Moving along second arc to END_2...")
        # await robot.move_on_circle(
        #     tcp_point_1=ARC_VIA_2,
        #     tcp_point_2=END_2,
        #     speed=ARC_2_SPEED,
        #     acceleration_duration=ARC_ACCELERATION_MS,
        #     arc_angle=0,
        #     blending_perc=0.0,
        # )
        # await wait_for_motion(robot, tag=6)

        # print(f"Pausing at END_2 for {END_PAUSE_SECONDS} second...")
        # await asyncio.sleep(END_PAUSE_SECONDS)

        # # 8. Arc from END_2 through ARC_VIA_2 to LOOK.
        # print("Returning along second arc to LOOK...")
        # await robot.move_on_circle(
        #     tcp_point_1=ARC_VIA_2,
        #     tcp_point_2=LOOK,
        #     speed=ARC_2_SPEED,
        #     acceleration_duration=ARC_ACCELERATION_MS,
        #     arc_angle=0,
        #     blending_perc=0.0,
        # )
        # await wait_for_motion(robot, tag=7)

        # 9. Move straight from LOOK to PARTICIPANT.
        print("Moving straight to PARTICIPANT...")
        await robot.move_to_point_line(
            tcp_point_goal=PARTICIPANT,
            speed=APPROACH_SPEED,
            acceleration_duration=ACCELERATION_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=8)

        # 10. Move straight from PARTICIPANT to HEAD_TILT.
        print("Moving straight to HEAD_TILT...")
        await robot.move_to_point_line(
            tcp_point_goal=HEAD_TILT,
            speed=APPROACH_SPEED,
            acceleration_duration=ACCELERATION_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=9)

        print(f"Pausing at HEAD_TILT for {HEAD_TILT_PAUSE_SECONDS} seconds...")
        await asyncio.sleep(HEAD_TILT_PAUSE_SECONDS)

        # 11. Move straight from HEAD_TILT back to PARTICIPANT.
        print("Moving straight back to PARTICIPANT...")
        await robot.move_to_point_line(
            tcp_point_goal=PARTICIPANT,
            speed=APPROACH_SPEED,
            acceleration_duration=ACCELERATION_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=10)

        # 12. Move straight from PARTICIPANT back to HOME.
        print("Moving straight back to HOME...")
        await robot.move_to_point_line(
            tcp_point_goal=HOME,
            speed=RETURN_SPEED_SLOW,
            acceleration_duration=RETURN_ACCELERATION_SLOW_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=11)

        print("Motion completed at HOME.")


if __name__ == "__main__":
    asyncio.run(main())
