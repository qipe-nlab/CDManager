# Slack CoolDown Manager: Usage Example

## Reaction: `Request` and `Withdraw`
Description: Put/Withdraw a request from the requested users queue.

### Usage:
1. Click on the `Request` button to if you want to want to use the fridge in the cooldown. Your name will appear in the `requested users` queue.
2. Click on the `Withdraw` button to if you want to cancel your request.


## Thread Message: Settle your experimental device
Description: Write a reply to the main board **INSIDE CODEBLOCK** to settle your experimental device.

### Usage:
1. If your request is approved by the users, you may add your device to the `Settle Queue` by replying to the main board with the following format:
```markdown
$ExperimentalDevice $ExperimentDescription
```
2. Send your command in the reply to the main board.
3. You may change the status of your device by editing the messge, **MODIFY** or **DELETE**.

<img src="./imgs/settled1.png" width=500>
<img src="./imgs/settled2.png" width=500>

## Command: `/cdm_open`
Description: Opens a new management board.

### Usage:
1. In any Slack channel or direct message, type `/cdm_open $CDNAME`.
2. Press Enter.
3. The app will initiate a new management board, providing you with request queue and settle queue.

<img src="./imgs/open1.png" width=500>

## Command: `/cdm_close`
Description: Closes the current management board.

### Usage:
1. After opening a board with `/cdm_open`, type `/cdm_close` in the same channel or direct message.
2. Press Enter.
3. The app will close the current board. The closed board will be archived and cannot be modified

## Command: `/cdm_force_abort`
Description: Forcefully aborts the current operation and removes the board from slack channel.

### Usage:
1. If this App does not behave as intended and restarting board is necessary, type `/cdm_force_abort 0000`.
2. The `0000` is a confirmation code that is provided when the board is initiated.
3. Press Enter.
3. The app will abort.
