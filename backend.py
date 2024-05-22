def get_body(params):
    cdname: str = params["cdname"]
    users_settled: dict = params["users_settled"]
    users_requested: dict = params["users_requested"]
    body_blocks = []

    section3_fields = []
    for i, (user_id, content) in enumerate(users_settled.items()):
        user_id = user_id.split("-")[0]
        user_d = {
            "type": "mrkdwn",
            "text": f"User{i+1}: <@{user_id}>\n- {content['device_name']}\n- {content['expriment_description']}",
        }
        section3_fields.append(user_d)

    if section3_fields == []:
        section3_fields.append({"type": "mrkdwn", "text": "No one has settled yet."})

    section2_text_base = []
    for user_id in users_requested:
        section2_text_base.append(f"<@{user_id}>")
    section2_text = ", ".join(section2_text_base)

    if section2_text_base == []:
        section2_text = "No one has requested yet."

    # header
    header1 = {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"{cdname}: Cooldown Management",
            "emoji": True,
        },
    }
    divider1 = {"type": "divider"}
    header2 = {
        "type": "header",
        "text": {"type": "plain_text", "text": "Requested", "emoji": True},
    }
    section_text2 = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": section2_text},
    }
    header3 = {
        "type": "header",
        "text": {"type": "plain_text", "text": "Settled", "emoji": True},
    }
    section_text3 = {
        "type": "section",
        "fields": section3_fields,
    }
    header4 = {
        "type": "header",
        "text": {"type": "plain_text", "text": "Reaction", "emoji": True},
    }
    request_section = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": ":white_check_mark: Request",
                    "emoji": True,
                },
                "value": "Request",
                "action_id": "want_to_use_fridge",
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": ":x: Withdraw",
                    "emoji": True,
                },
                "value": "Skip",
                "action_id": "skip_fridge",
            },
        ],
    }

    body_blocks = [
        header1,
        header2,
        section_text2,
        divider1,
        header3,
        section_text3,
        header4,
        request_section,
    ]
    return body_blocks