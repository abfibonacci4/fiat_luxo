
import asyncio

import techmanpy

ROBOT_IP = "172.16.8.2"

# Replace with a previously taught and validated target pose.
# TARGET_B = [-160.61, 40.72, 758.60, -158.12, 10.11, 131.40]

# TARGET_B = [-150.77, -77.20, 598.27, -102.19, 1.97, -148.95]
TARGET_B = [-259.13, -89.25, 573.31, -163.75, 17.14, 145.85]
# TARGET_B = [-259.13, -89.25, 573.31, -163.75, 17.14, 145.85]


SPEED_PERCENT = 0.25
ACCELERATION_MS = 1000


async def move_to_pose(target: list[float]) -> None:
    if len(target) != 6:
        raise ValueError("Target pose must contain six values.")

    async with techmanpy.connect_sct(robot_ip=ROBOT_IP) as robot:
        await robot.move_to_point_ptp(
            tcp_point_goal=target,
            speed_perc=SPEED_PERCENT,
            acceleration_duration=ACCELERATION_MS,
            blending_perc=0,
        )


async def main() -> None:
    if TARGET_B is None:
        raise ValueError(
            "Set TARGET_B to a verified, collision-free "
            "Cartesian target before running."
        )

    print(f"Target: {TARGET_B}")
    confirmation = input(
        "Type MOVE after verifying the workspace and target: "
    )

    if confirmation != "MOVE":
        print("Motion cancelled.")
        return

    await move_to_pose(TARGET_B)
    print("Motion command submitted.")


if __name__ == "__main__":
    asyncio.run(main())
