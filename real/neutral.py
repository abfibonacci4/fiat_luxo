
import asyncio
import math

import techmanpy


ROBOT_IP = "172.16.8.2"

HOME = [-160.61, 40.72, 758.60, -158.12, 10.11, 131.40]
LOOK = [-274.97, -104.98, 487.96, -135.26, 17.42, 147.06]

SPEED_PERCENT = 0.65
ACCELERATION_MS = 500
PAUSE_SECONDS = 2.0


async def move_to_pose(robot, target: list[float], tag: int) -> None:
    if len(target) != 6 or not all(math.isfinite(x) for x in target):
        raise ValueError("Target must contain six finite values.")

    await robot.move_to_point_ptp(
        tcp_point_goal=target,
        speed_perc=SPEED_PERCENT,
        acceleration_duration=ACCELERATION_MS,
        blending_perc=0.0,
    )

    # Wait until the queued motion has completed.
    await robot.set_queue_tag(tag, wait_for_completion=True)


async def neutral_motion() -> None:
    print("Neutral motion: HOME -> LOOK -> HOME")

    confirmation = input(
        "Type MOVE after validating all three motion segments: "
    )

    if confirmation != "MOVE":
        print("Cancelled.")
        return

    async with techmanpy.connect_sct(robot_ip=ROBOT_IP) as robot:
        print("Moving to HOME...")
        await move_to_pose(robot, HOME, tag=1)

        print("Moving to LOOK...")
        await move_to_pose(robot, LOOK, tag=2)

        print(f"Waiting {PAUSE_SECONDS} seconds...")
        await asyncio.sleep(PAUSE_SECONDS)

        print("Returning HOME...")
        await move_to_pose(robot, HOME, tag=3)

        print("Neutral motion completed.")


if __name__ == "__main__":
    asyncio.run(neutral_motion())