
import asyncio
import math

import techmanpy


ROBOT_IP = "172.16.8.2"

# HOME = [-160.61, 40.72, 758.60, -158.12, 10.11, 131.40]
HOME = [-259.13, -89.25, 573.31, -163.75, 17.14, 145.85]
# HOME = [-167.42, 27.38, 775.38, -163.39, 4.55, 130.15]
# HOME = [-179.44, -42.35, 696.34, -162.67, 8.47, 131.10]
# LOOK = [-274.97, -104.98, 487.96, -135.26, 17.42, 147.06]
LOOK = [-256.15, -86.56, 433.84, -152.37, 14.73, 149.03]


SPEED_PERCENT = 0.50
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