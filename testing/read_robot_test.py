
import asyncio

import techmanpy

ROBOT_IP = "172.16.8.2"


def on_robot_data(data: dict) -> None:
    joint_angles = data.get("Joint_Angle")

    if joint_angles is not None:
        print("Joint angles:", joint_angles)


async def main() -> None:
    async with techmanpy.connect_svr(robot_ip=ROBOT_IP) as robot:
        robot.add_broadcast_callback(on_robot_data)
        await robot.keep_alive()


if __name__ == "__main__":
    asyncio.run(main())
