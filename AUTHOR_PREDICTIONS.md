# Predictions

## Classes

- V0: Successful response, text container present, zero visible UTF-8 bytes, recognized normal stop.
- V1: Successful response, zero visible UTF-8 bytes, recognized output-budget stop.
- V2: Successful response, text container absent, zero visible UTF-8 bytes, recognized normal stop.
- VU: Successful response, zero visible UTF-8 bytes, termination state not mapped by the frozen protocol.
- NV: Nonempty text consisting only of frozen invisible characters or whitespace, or whose stripped form is one of the frozen ellipsis forms.
- R: Nonempty visible text under the frozen classifier.
- RF: Refusal reported by a distinct provider field.
- SB: Safety block reported by a distinct provider field.
- TC: Tool call reported by a distinct provider field.
- operational: Error rather than a successful response.

## Fixed inputs

- Witness question: "What is 2 + 2?"
- System prompt: "Answer with the shortest correct answer. Do not add punctuation."
- Maximum new tokens per request: 4.
- Both runs use fresh model execution under the live SwiftAPI authority.
- The secondary population is the 188 questions in evidence/bank.json from sharthokrayanpal/PCCG-2-Qwen3-4B at revision a3b952458a46b5547ba3cec7d03a37b395bed03a, in file order.

## Format

Each prediction is one result line: [arm] [model identifier] [count/total] [class].
The command under each arm reads that arm from a completed run and dispatches no request.
The seal is the SHA-256 of the exact bytes of this file.

## Run 1: PRIMARY WITNESS_ONE

### VALID

Arm VALID: The known key and an unmodified grant issued for this exact request are sent. What will the result line be?

`[VALID] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [R]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm VALID`

### SIGNED_DENIAL

Arm SIGNED_DENIAL: The known key and the authority object returned for an unknown action type with strict_action_type enabled are sent. What will the result line be?

`[SIGNED_DENIAL] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm SIGNED_DENIAL`

### MISSING_GRANT

Arm MISSING_GRANT: The known key and an explicit null grant are sent. What will the result line be?

`[MISSING_GRANT] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm MISSING_GRANT`

### INVALID_SIGNATURE

Arm INVALID_SIGNATURE: The known key and an issued grant whose signature has been replaced are sent. What will the result line be?

`[INVALID_SIGNATURE] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm INVALID_SIGNATURE`

### EXPIRED

Arm EXPIRED: The known key and an issued grant are sent after waiting beyond its registered age limit. What will the result line be?

`[EXPIRED] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm EXPIRED`

### REUSED

Arm REUSED: The known key, request identifier and grant already submitted in the earlier VALID arm are sent again. What will the result line be?

`[REUSED] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm REUSED`

### WRONG_SCOPE

Arm WRONG_SCOPE: The known key and an authority-issued grant for the connection-check scope are sent to the native request. What will the result line be?

`[WRONG_SCOPE] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm WRONG_SCOPE`

### WRONG_REQUEST

Arm WRONG_REQUEST: The known key and an issued grant are sent with a different request identifier. What will the result line be?

`[WRONG_REQUEST] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm WRONG_REQUEST`

### UNKNOWN_KEY

Arm UNKNOWN_KEY: A syntactically formed key not issued to the run and an explicit null grant are sent. What will the result line be?

`[UNKNOWN_KEY] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [operational]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm UNKNOWN_KEY`

### MALFORMED_KEY

Arm MALFORMED_KEY: A malformed key string and an explicit null grant are sent. What will the result line be?

`[MALFORMED_KEY] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [operational]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm MALFORMED_KEY`

### REVOKED

Arm REVOKED: The known key and one disposable grant are sent after that grant has been submitted to the revocation endpoint. What will the result line be?

`[REVOKED] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_PRIMARY.json --out PRIMARY_OUTPUT --arm REVOKED`

## Run 2: SECONDARY BANK_188

### VALID

Arm VALID: The known key and an unmodified grant issued for this exact request are sent. What will the result line be?

`[VALID] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [188/188] [R]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_SECONDARY.json --out SECONDARY_OUTPUT --arm VALID`

### MISSING_GRANT

Arm MISSING_GRANT: The known key and an explicit null grant are sent. What will the result line be?

`[MISSING_GRANT] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [188/188] [V0]`

`python -m swiftapi_native_service.experiment question --config RUN_CONFIG_SECONDARY.json --out SECONDARY_OUTPUT --arm MISSING_GRANT`
