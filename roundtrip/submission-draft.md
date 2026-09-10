# Roundtrip — submission form draft

Prepared from the user-supplied form screenshot on September 10, 2026. Proposed separate submission; final text should match the recorded demo.

## Project Description

Roundtrip helps independent photographers turn feedback into finished edits while keeping the human connection at the heart of photography. For headshots and family portraits, our premise is that the real sitting, the camera and the photographer's choices matter. Roundtrip uses no image-generation model. Instead, Astra interprets feedback and operates Lightroom's native editing controls on the actual photograph, saves a new version, and returns an export for comparison. Originals and prior exports remain available, and the photographer decides what feels right. The goal is faster revision turnaround with the photographer's eye still guiding the result.

## Describe your use of OpenAI products to build the submitted project.

I used GPT-6 Astra in Codex to build the review gallery, feedback-to-edit workflow, revision history, interface and verification checks, iterating with real photographs and observed Lightroom behavior.

At runtime, a local job launches Astra through Codex to inspect the source photograph, interpret feedback and operate Lightroom through computer use. It applies native adjustments such as light, color, cropping and masks, saves a named version, exports a JPEG and inspects the result. The application verifies the returned export before adding it to the gallery. Astra supplies visual reasoning and tool use; no image-generation model is used to synthesize a replacement picture. The demonstrated editing loop runs through Lightroom on the photographer's Mac.

## Provide feedback from your experience using OpenAI products.

Suggested wording for the user's review:

Astra's ability to interpret a visual request and then work in an existing professional application was the most compelling part of this project. It made a useful loop possible between feedback, native Lightroom edits and a reviewable export. Reliability still depended on careful photo identification and application state: an early attempt stopped after Lightroom moved to a different photograph, and a successful retry followed manual restoration. Clearer persistent application targeting and easier recovery from interface-state changes would make this workflow stronger. My role remained choosing the desired look and judging the returned photograph.

## Evidence before final submission

The local native-Lightroom loop has been verified. Hosted end-to-end delivery is not established. A successful studio-portrait retry took 289.7 seconds after manual preparation; label compressed footage honestly. Audience preference and faster turnaround are product hypotheses, not measured customer outcomes. Do not claim that all inference or data processing stays on the Mac.

## Team and links

Team name: Token Party. The supplied form screenshot shows Ezra Mechaber as a member. Public GitHub repository URL and one-minute demo URL still need to be inserted and verified. The screenshot does not establish that multiple submissions are permitted. No form fields were filled or submitted by this session.
