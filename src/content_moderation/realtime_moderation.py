from content_moderation.moderator import moderate_text

def moderate_multiplayer_message(
    player_id,
    message,
    channel="text"
):
    result = moderate_text(message)

    moderation_result = {
        "player_id": player_id,
        "channel": channel,
        "message": message,
        "moderation": result
    }

    return moderation_result


if __name__ == "__main__":

    live_messages = [
        {
            "player_id": "PLAYER-1001",
            "channel": "text",
            "message": "nice shot well played"
        },
        {
            "player_id": "PLAYER-2002",
            "channel": "text",
            "message": "you are stupid"
        },
        {
            "player_id": "PLAYER-3003",
            "channel": "voice_transcript",
            "message": "shut up loser"
        }
    ]

    print("=" * 60)
    print(
        "GameShield AI - Real-Time "
        "Multiplayer Moderation"
    )
    print("=" * 60)

    for live_message in live_messages:

        result = moderate_multiplayer_message(
            live_message["player_id"],
            live_message["message"],
            live_message["channel"]
        )

        moderation = result["moderation"]

        print("\nLive Message")
        print("-" * 60)

        print(
            f"Player: "
            f"{result['player_id']}"
        )

        print(
            f"Channel: "
            f"{result['channel']}"
        )

        print(
            f"Message: "
            f"{result['message']}"
        )

        print(
            f"Decision: "
            f"{moderation['action']}"
        )

        print(
            f"Status: "
            f"{moderation['status']}"
        )