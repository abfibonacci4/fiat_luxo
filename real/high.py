
import asyncio
import math

import techmanpy


ROBOT_IP = "172.16.8.2"

HOME = [-259.13, -89.25, 573.31, -163.75, 17.14, 145.85]
LOOK = [-256.15, -86.56, 433.84, -152.37, 14.73, 149.03]
BACK = [-216.55, -46.94, 505.93, -139.99, 11.37, 151.82]
NOD_UP = [-217.37, -47.69, 536.98, -128.55, 7.69, 153.70]
ARC_VIA = [-238.46, -68.79, 574.19, -136.77, 10.39, 152.43]

LOOK_SPEED = 0.8
APPROACH_SPEED = 0.5
RETURN_SPEED = 0.8
ACCELERATION_MS = 500
RETURN_ACCELERATION_MS = 250
LOOK_ACCELERATION_MS = 500
PAUSE_SECONDS = 2.0
PARTICIPANT_PAUSE_SECONDS = 0.25

# Independent nod settings.
# Start conservatively and increase only after validating the motion.
NOD_SPEED = 1.0
NOD_ACCELERATION_MS = 250
NOD_REPETITIONS = 2


def validate_pose(pose: list[float]) -> None:
    if len(pose) != 6 or not all(math.isfinite(x) for x in pose):
        raise ValueError("Pose must contain six finite values.")


async def wait_for_motion(robot, tag: int) -> None:
    await robot.set_queue_tag(tag, wait_for_completion=True)


async def move_to_pose(
    robot,
    target: list[float],
    speed: float,
    acceleration_ms: int,
    tag: int,
) -> None:
    await robot.move_to_point_ptp(
        tcp_point_goal=target,
        speed_perc=speed,
        acceleration_duration=acceleration_ms,
        blending_perc=0.0,
    )
    await wait_for_motion(robot, tag)


async def neutral_motion() -> None:
    for pose in (HOME, LOOK, BACK, ARC_VIA, NOD_UP):
        validate_pose(pose)

    print(
        "Motion: HOME -> LOOK -> ARC -> BACK -> PARTICIPANT "
        "-> BACK -> NOD_UP -> BACK -> NOD_UP -> BACK -> HOME"
    )

    confirmation = input(
        "Type MOVE after validating all motion segments: "
    )

    if confirmation != "MOVE":
        print("Cancelled.")
        return

    async with techmanpy.connect_sct(robot_ip=ROBOT_IP) as robot:
        # 1. Move to HOME.
        print("Moving to HOME...")
        await move_to_pose(
            robot, HOME, APPROACH_SPEED, ACCELERATION_MS, tag=1
        )

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

        # 4. Move from LOOK to BACK along an arc.
        print("Moving along arc from LOOK to BACK...")
        await robot.move_on_circle(
            tcp_point_1=ARC_VIA,
            tcp_point_2=BACK,
            speed=RETURN_SPEED,
            acceleration_duration=RETURN_ACCELERATION_MS,
            arc_angle=0,
            blending_perc=0.0,
        )
        await wait_for_motion(robot, tag=3)

        # # 5. Move from BACK to PARTICIPANT.
        # print("Moving to PARTICIPANT...")
        # await move_to_pose(
        #     robot, PARTICIPANT, LOOK_SPEED,
        #     LOOK_ACCELERATION_MS, tag=4
        # )

        # # 6. Pause at PARTICIPANT.
        # print(
        #     f"Pausing for {PARTICIPANT_PAUSE_SECONDS} seconds..."
        # )
        # await asyncio.sleep(PARTICIPANT_PAUSE_SECONDS)

        # # 7. Return from PARTICIPANT to BACK.
        # print("Returning to BACK...")
        # await move_to_pose(
        #     robot, BACK, LOOK_SPEED,
        #     LOOK_ACCELERATION_MS, tag=5
        # )

        # 8. Perform two nods: BACK -> NOD_UP -> BACK.
        for nod_index in range(NOD_REPETITIONS):
            print(f"Performing nod {nod_index + 1}/{NOD_REPETITIONS}...")

            up_tag = 6 + nod_index * 2
            down_tag = up_tag + 1

            await move_to_pose(
                robot, NOD_UP, NOD_SPEED,
                NOD_ACCELERATION_MS, tag=up_tag
            )

            await move_to_pose(
                robot, BACK, NOD_SPEED,
                NOD_ACCELERATION_MS, tag=down_tag
            )

        # 9. Return from BACK to HOME.
        print("Returning to HOME...")
        await move_to_pose(
            robot, HOME, APPROACH_SPEED,
            ACCELERATION_MS, tag=10
        )

        print("Motion sequence completed.")


if __name__ == "__main__":
    asyncio.run(neutral_motion())
