
import asyncio
import math

import techmanpy


ROBOT_IP = "172.16.8.2"

HOME = [-259.13, -89.25, 573.31, -163.75, 17.14, 145.85]
LOOK = [-256.15, -86.56, 433.84, -152.37, 14.73, 149.03]
ARC_VIA_1 = [-304.88, -161.19, 436.38, -172.07, 15.62, 172.75]
END_1 = [-467.05, -243.44, 334.48, -135.80, 16.65, -127.16]
ARC_VIA_2 = [-453.81, -351.57, 391.40, -151.50, 34.60, -127.84]
END_2 = [-409.74, -459.47, 517.37, 144.34, 10.50, 150.97]

ARC_VIA_3 = [-222.33, -547.65, 402.79, 133.93, 6.25, 174.64]
END_3 = [-26.60, -444.55, 348.61, 133.26, -1.39, -115.75]
ARC_VIA_4 = [-163.26, -277.56, 603.75, -172.32, -6.74, -163.19]
PARTICIPANT = [-135.53, -206.33, 542.94, -96.30, -4.28, -162.58]
HEAD_SHAKE = [-162.82, -210.99, 542.01, -96.79, -5.91, -176.50]
HEAD_LOW = [-136.60, -214.40, 368.76, -164.95, 20.58, -174.01]
LOW_SHAKE = [-187.36, -210.71, 360.34, -169.05, -4.94, -179.84]


LOOK_SPEED = 0.5
APPROACH_SPEED = 0.4
ARC_1_SPEED = 0.3
ARC_2_SPEED = 0.3
ARC_3_SPEED = 0.3
ARC_4_SPEED = 0.3
RETURN_SPEED = 0.5
RETURN_SPEED_SLOW = 0.3


ACCELERATION_MS = 500
RETURN_ACCELERATION_MS = 500
RETURN_ACCELERATION_SLOW_MS = 800
LOOK_ACCELERATION_MS = 500
ARC_ACCELERATION_MS = 800

PAUSE_SECONDS = 2.0
ARC_PAUSE_SECONDS = 1.0
HEAD_LOW_PAUSE_SECONDS = 1.0

# Independent head-shake settings.
SHAKE_SPEED = 1.0
SHAKE_ACCELERATION_MS = 250
SHAKE_REPETITIONS = 2


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


async def main() -> None:
    for pose in (
        HOME,
        LOOK,
        ARC_VIA_1,
        END_1,
        ARC_VIA_2,
        END_2,
        ARC_VIA_3,
        END_3,
        ARC_VIA_4,
        PARTICIPANT,
        HEAD_SHAKE,
        HEAD_LOW,
        LOW_SHAKE,
    ):
        validate_pose(pose)

    print(
        "Motion: HOME -> LOOK -> ARC_VIA_1 -> END_1 "
        "-> ARC_VIA_2 -> END_2 -> ARC_VIA_3 -> END_3 "
        "-> ARC_VIA_4 -> LOOK -> PARTICIPANT -> HEAD_SHAKE "
        "-> PARTICIPANT -> HEAD_LOW -> HOME"
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

        # 4. Chain four arcs from LOOK back to LOOK.
        print("Moving along arc 1 to END_1...")
        await robot.move_on_circle(
            tcp_point_1=ARC_VIA_1,
            tcp_point_2=END_1,
            speed=ARC_1_SPEED,
            acceleration_duration=ARC_ACCELERATION_MS,
            arc_angle=0,
            blending_perc=0.0,
        )
        await wait_for_motion(robot, tag=3)
        print(f"Pausing at END_1 for {ARC_PAUSE_SECONDS} second...")
        await asyncio.sleep(ARC_PAUSE_SECONDS)

        print("Moving along arc 2 to END_2...")
        await robot.move_on_circle(
            tcp_point_1=ARC_VIA_2,
            tcp_point_2=END_2,
            speed=ARC_2_SPEED,
            acceleration_duration=ARC_ACCELERATION_MS,
            arc_angle=0,
            blending_perc=0.0,
        )
        await wait_for_motion(robot, tag=4)
        print(f"Pausing at END_2 for {ARC_PAUSE_SECONDS} second...")
        await asyncio.sleep(ARC_PAUSE_SECONDS)

        print("Moving along arc 3 to END_3...")
        await robot.move_on_circle(
            tcp_point_1=ARC_VIA_3,
            tcp_point_2=END_3,
            speed=ARC_3_SPEED,
            acceleration_duration=ARC_ACCELERATION_MS,
            arc_angle=0,
            blending_perc=0.0,
        )
        await wait_for_motion(robot, tag=5)
        print(f"Pausing at END_3 for {ARC_PAUSE_SECONDS} second...")
        await asyncio.sleep(ARC_PAUSE_SECONDS)

        print("Moving along arc 4 back to LOOK...")
        await robot.move_on_circle(
            tcp_point_1=ARC_VIA_4,
            tcp_point_2=LOOK,
            speed=ARC_4_SPEED,
            acceleration_duration=ARC_ACCELERATION_MS,
            arc_angle=0,
            blending_perc=0.0,
        )
        await wait_for_motion(robot, tag=6)

        # 5. Move straight from LOOK to PARTICIPANT.
        print("Moving straight to PARTICIPANT...")
        await robot.move_to_point_line(
            tcp_point_goal=PARTICIPANT,
            speed=APPROACH_SPEED,
            acceleration_duration=ACCELERATION_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=7)

        # # 6. Shake "no": PARTICIPANT -> HEAD_SHAKE -> PARTICIPANT.
        # for shake_index in range(SHAKE_REPETITIONS):
        #     print(
        #         f"Performing head shake {shake_index + 1}/{SHAKE_REPETITIONS}..."
        #     )
        #     shake_tag = 8 + shake_index * 2
        #     participant_tag = shake_tag + 1

        #     await move_to_pose(
        #         robot,
        #         HEAD_SHAKE,
        #         SHAKE_SPEED,
        #         SHAKE_ACCELERATION_MS,
        #         tag=shake_tag,
        #     )
        #     await move_to_pose(
        #         robot,
        #         PARTICIPANT,
        #         SHAKE_SPEED,
        #         SHAKE_ACCELERATION_MS,
        #         tag=participant_tag,
        #     )

        # # 7. Move straight from PARTICIPANT to HEAD_LOW.
        # print("Moving straight to HEAD_LOW...")
        # await robot.move_to_point_line(
        #     tcp_point_goal=HEAD_LOW,
        #     speed=APPROACH_SPEED,
        #     acceleration_duration=ACCELERATION_MS,
        #     blending=0.0,
        # )
        # await wait_for_motion(robot, tag=8 + SHAKE_REPETITIONS * 2)
        # print(f"Pausing at HEAD_LOW for {HEAD_LOW_PAUSE_SECONDS} second...")
        # await asyncio.sleep(HEAD_LOW_PAUSE_SECONDS)

        # # 8. Move straight from HEAD_LOW back to HOME.
        # print("Moving straight back to HOME...")
        # await robot.move_to_point_line(
        #     tcp_point_goal=HOME,
        #     speed=RETURN_SPEED_SLOW,
        #     acceleration_duration=RETURN_ACCELERATION_SLOW_MS,
        #     blending=0.0,
        # )
        # await wait_for_motion(robot, tag=9 + SHAKE_REPETITIONS * 2)

        # Alternative post-participant sequence: use this block instead of
        # steps 6-8 above to shake between HEAD_LOW and LOW_SHAKE.
        print("Moving straight to HEAD_LOW...")
        await robot.move_to_point_line(
            tcp_point_goal=HEAD_LOW,
            speed=APPROACH_SPEED,
            acceleration_duration=ACCELERATION_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=8)
        
        for shake_index in range(SHAKE_REPETITIONS):
            print(
                f"Performing low head shake "
                f"{shake_index + 1}/{SHAKE_REPETITIONS}..."
            )
            shake_tag = 9 + shake_index * 2
            head_low_tag = shake_tag + 1
        
            await move_to_pose(
                robot,
                LOW_SHAKE,
                SHAKE_SPEED,
                SHAKE_ACCELERATION_MS,
                tag=shake_tag,
            )
            await move_to_pose(
                robot,
                HEAD_LOW,
                SHAKE_SPEED,
                SHAKE_ACCELERATION_MS,
                tag=head_low_tag,
            )
        
        print(
            f"Pausing after low head shakes for "
            f"{HEAD_LOW_PAUSE_SECONDS} second..."
        )
        await asyncio.sleep(HEAD_LOW_PAUSE_SECONDS)
        
        print("Moving straight back to HOME...")
        await robot.move_to_point_line(
            tcp_point_goal=HOME,
            speed=RETURN_SPEED_SLOW,
            acceleration_duration=RETURN_ACCELERATION_SLOW_MS,
            blending=0.0,
        )
        await wait_for_motion(robot, tag=9 + SHAKE_REPETITIONS * 2)

        print("Motion completed at HOME.")


if __name__ == "__main__":
    asyncio.run(main())
