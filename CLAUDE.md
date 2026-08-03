# Client Hub — operating instructions

This is the operating file for Abba Photo client engagement hubs: live, client-facing GitHub Pages sites. A copy of this file sits in every client hub repo. Any Claude session working in a hub repo (cloud or CLI) follows these rules.

## The job
`index.html` is the single working plan the client's whole team reads. It updates as the engagement moves: client notes fold in, sample images land, sections change. The live URL never changes.

## Update workflow
1. Edit `index.html` directly. All copy lives between the tags; CSS is at the top of the file.
2. Commit and push to `main`. GitHub Pages redeploys in about a minute.
3. Verify: fetch the live URL and check for your change. If network egress blocks the fetch, check the Pages deploy status through the GitHub API instead.
4. Log what changed and why in `STATE.md`: one line, date first, newest at the top of the log.

## Intake loop
Client notes arrive by email at noah@abba-photo.com (engagement specifics are in `STATE.md`; contact addresses live in the private `abba-dashboard` repo, `docs/CLIENT_CONTACTS.md`). When asked to process intake: read the new messages through the Gmail connector, fold the substance into the page or record it in `STATE.md` as pending, push, and stage (never send) any reply a question requires. Sending email is always the owner's click.

## Voice (hard rules)
- No em dashes, anywhere, ever.
- No bravado. State the unique fact, never the verdict or superlative. The work makes the claim.
- The owner's own phrasings are canon. Do not polish them into generic copy.
- Plain sentences. No "it's not X, it's Y" reversals, no rule-of-three flourishes, no hollow intensifiers.

## Client-page boundary
The page is read by the client's whole team and the repo is public. Never put on the page or in this repo: pricing or any money amount, contact addresses or phone numbers, booking/confirmation references, personal-circumstance context, internal notes, other clients' names, or client details that are not yet public (campaign themes, gifts, donor names, unannounced plans). All of those live in the private `abba-dashboard` repo at `docs/CLIENT_CONTACTS.md`; this repo carries only a pointer. If a client note references something that does not already appear on the page, ask the owner before publishing it. When in doubt, leave it off.

## Images
Cloud sandboxes are Linux: use Python/Pillow, not sips.

    python3 -c "from PIL import Image; im=Image.open('in.jpg'); im.thumbnail((1400,1400)); im.save('img/out.jpg', quality=82)"

Web images live in `img/` and are referenced relatively. No camper or minor faces on a public page unless `STATE.md` confirms releases.

## Approval gates
- Sending any email: owner's click, always. Drafts stage freely.
- Creating any new public repo or page: one explicit OK from the owner.
- Page edits inside an active engagement: pre-approved. Push freely and verify.
