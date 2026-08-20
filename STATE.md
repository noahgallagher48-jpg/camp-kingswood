# Engagement state: Camp Kingswood

Read this together with CLAUDE.md before touching the page. Log entries at the
bottom, one line each, newest first. This file is public with the repo: nothing
goes in it that the client has not made public.

## Facts a session needs
- Engagement: full residency, arrival Wednesday evening August 5 through Sunday
  August 9, 2026, on site at Camp Kingswood, Bridgton, Maine. Booked 2026-08-02; dates settled at
  Aug 5-9 on 2026-08-03.
- Client contact: Jodi Sperling, Owner/Director. Contact details and money terms
  live in the private `abba-dashboard` repo (`docs/CLIENT_CONTACTS.md` and
  `docs/KINGSWOOD_AGREEMENT_DRAFT.md`), not here.
- DELIVERABLES ARE OPEN (Noah, night of 8/4): the agreement is SENT but NOT SIGNED.
  Jodi confirmed the dates and asked to talk through the deliverables; that conversation
  is the residency's first item (page carries a "First, the deliverables" section; a
  check-off email to her is staged for Noah's send, cc her assistant). Until settled,
  the list below is the working shape from the sent agreement, not final. Anything a
  session writes about deliverables STAGES and escalates.
- Working shape (from the sent agreement): the forty-two (twelve mastered
  campscapes and thirty storytelling candids) by Aug 23, additional usable images
  included; the camp's summer media library closed and organized with
  written instructions by Aug 30; two photo books scoped on site (layouts for the
  camp's approval); a community print store to follow.
- The media team shoots alongside Noah all weekend; support framing is the
  engagement's condition. Do not name the team members on this page.
- The walk: camp provides walking companions with long attachment to Kingswood.
- AUTHOR MODE (owner, 2026-08-03): no specific assignments, no shot lists. The
  camp's team covers daily camp; the owner captures what is special. If a
  shot-list or assignment request arrives by email, that is SCOPE: stage the
  reply and escalate, never absorb it into the plan.
- Releases NOT confirmed: no camper or minor faces on this page until STATE
  records the camp's confirmation.
- No donor or patron names on this page, ever (the dedicated book's recipients
  are named only in private docs).

## Intake loop
Questions from the client arrive at noah@abba-photo.com. NOTE: the twice-daily sweep
is PAUSED since 8/3, so intake is live sessions and manual sweeps only during the
residency; check the inbox at session start. Answer what the agreement and this page
already settle. SCOPED SEND GRANT (owner, 2026-08-03): from August 5 through
August 10, replies to the client OR HER DESIGNEE (IDENTIFIED 8/4: her assistant, per her auto-reply; address in the private contacts file) that are purely logistics or schedule may SEND
directly without per-email approval; every such send logs a one-line resolution
in this file's log AND on the owner's board in the same session. Anything
touching money, scope, deliverables, or people STAGES as a draft and escalates
to the owner with a push notification, as always. Outside that window, all
replies stage. Context for the grant: the owner shoots midnight to dawn during
the residency and rests in daytime pockets, so client communication must not
wait on his hours; the loop answers while he is dark. Text messages to the owner's phone are invisible to this loop; the
owner relays them (screenshot or paste) to the same inbox.

## Log
- 2026-08-19 (SET COMPLETE): the client's Drive folder is now exactly the 117 delivered frames plus the web zip, all carrying the credential block. Drive became a LOCAL MOUNT this session (Drive for Desktop, noah@abba-photo.com), so the sync is plain cp and file IDs survive an overwrite, which is why every published per-frame link kept working. The ten set-aside frames were MOVED, not deleted, to Kingswood/_aside_not_delivered (owner-only, invisible to the camp; nothing lost). Six re-edit frames mapped and verified, so all 117 now carry full-res links. Zip wired as a file-VIEW url, not uc?export=download: Drive serves a virus-scan interstitial instead of the file above ~100MB. Routine at hub/drive_sync.sh (check | push) so the folder can never drift again unnoticed. Verified: 117 on Drive, aside invisible, all six re-edits resolve, zip and folder pages public with no sign-in wall, page live with zero null links.
- 2026-08-19 (WEB TIER RULE, standing): a delivered "web" file is 3840px long edge, q90, 4:4:4, sRGB, from the masters, credit-stacked. His words: "I can't have these garbage files calling themselves web res." The first build shipped the 2560/q88 display tier (~1-2MB) as the client download; that tier is page furniture, never a deliverable. New img/web tier built for all 127 (avg 3.2MB, range 1.1-7.5), credit-stacked, pool-only 117 committed. Every Web button and the zip now point at img/web; zip rebuilt at 372MB (git-ignored, waits on the Drive upload). Rule written into ~/.claude/skills/photo-web-processing/SKILL.md so it binds every future delivery. Verified live: 3072x3840, 3.6MB, credits read back, buttons hand over 5-6MB files.
- 2026-08-19 (delivery page LIVE): delivery.html built and pushed, Interlaken structure in Kingswood colors (navy #0E1B2C ground, vermilion #DB3A00 accent, warm white ink). Pool = 117 per the arrangement (121 minus 10 aside plus 6 re-edits); picks reader = 44 (frames 39 and 117 sat in both his top choices and the aside list; aside won, so they dropped from the picks too, flagged to the owner). Sections: Play (fullscreen picks slideshow, stripped zones, black stage pixel-verified), All full res (Drive folder), Select frames (per-frame Web + Full res), Everything grid in shoot order, lightbox. Pool-only tiers committed with add -f; the 10 aside frames stay unpublished. Live at https://www.abba-photo.com/camp-kingswood/delivery.html, noindex, NOT linked from index.html yet. Verified: 161/161 images decode live, EXIF credits read back off the deployed file. Pool zip rebuilt for 117 (153MB, downloads/, git-ignored) and waits for the owner's Drive upload; ZIP_URL in build_delivery.py takes its uc id and the All-for-web button appears on rebuild. Full res for frames 201-206 pending the owner's six-file Drive drag.
- 2026-08-19 (owner's pass ON THE RECORD): arrangement exported and saved to _work/arrangement_kw.json; it now seeds every rebuild. His top choices: "Proposed forty-two" grown to 46 (counts are floors). SET ASIDE = REPLACED, his words: "set aside should be replaced with the _2 set with the others": the 10 aside frames (72,120,77,116,117,111,114,113,71,39) come out of the delivery pool; the six _2 re-edit exports come in (kwood819_2 series, frames 201-206; numbering fixed so _2-N parses as 200+N, not N). The _2 set is EXIF-processed, in masters_delivery (127 files), ingested (127 tiers), and surfaces on the arrange board as "New since your last pass" (standing rule: frames ingested after a saved pass get their own group). Full decode audit: 233/233 tiles, zero failures. OPEN AT BUILD: confirm the final delivery pool (121 minus 10 aside plus 6 new = 117) and whether the aside frames' Drive copies come out; note 39 and 117 sit in both aside and his groups, resolve at build.
- 2026-08-19 (releases + arrange): RELEASES ARE NOT CONNECTED TO THIS DELIVERY (Noah). Delivering a camp photographs of its own community is not publication; the camp holds that relationship. The gate is out of build_delivery.py and out of the runbook. A frame moving to one of Noah's OWN promotional surfaces stays a separate decision. ARRANGE TOOL built (build_arrange.py), ported from the Interlaken arrange page at his direction ("that was the best interface for this"): all 121 frames, drag and drop, create/rename/reorder/delete groups, groups hold COPIES so a frame lives in as many as it needs, tap path mirrors drag, drag-dock on the right, gold badge counts group membership, Set aside lane, Copy the arrangement exports JSON. Seeded with the proposed forty-two plus three observed runs (Shabbat, The sign, Night and stars), all deletable; no quota. Local build _work/arrange.html (full-size viewer), portable published as a private artifact. THE RECORD: paste his exported arrangement back and it saves to _work/arrangement_kw.json, which then seeds every later build (localStorage alone does not survive a device or origin change).
- 2026-08-19 (selection tool): Drive swap VERIFIED, the folder now holds the processed masters (byte-match to masters_delivery; prior file IDs gone). build_select.py added: every frame pickable, picks persist per device, Play runs the picks as a preview slideshow with drop-from-slideshow. Two builds, local (full-res off img/present) and portable (760px embedded, published as a private artifact). Draft forty-two pre-loaded as the starting selection, awaiting the owner's pass. .gitignore added: img tiers, downloads, _work, forty_two.json, links.json and masters can never be committed to this public repo by accident. Frame numbering note: the bare kwood819.jpg is frame 1 (house convention); numbers otherwise 2 to 122, 83 absent from the export.
- 2026-08-19 (later): Drive full-res folder link received and verified: the uploaded files are the UNPROCESSED export (byte-match to ~/Abba_Photo/kwood819, Lightroom/C2PA metadata intact). Owner re-drags from ~/Desktop/ABBA/kingswood/masters_delivery (processed, same filenames, same share link) after deleting the folder's current contents. Web tiers credit-stacked; kingswood_web.zip built (156MB). links.json and forty_two.json held LOCAL, out of git, until the releases decision; the Drive link reaches no public surface before that gate clears.
- 2026-08-19 (owner dispositions, by voice): ALL 121 deliver; the two B&W and every flagged frame stay ("No objections to the frames. They look great."); Jodi decides usage, "there's more than she needs here." Frame 16 tagged POTENTIAL COVER WITH TEXT (heard as "sixty," read as sixteen from context; owner corrects if 60 was meant). DRAFT forty_two.json written (Claude's proposed 12 scapes + 30 candids) awaiting owner's kill/swap pass on the review gallery. Masters copy EXIF-processed at ~/Desktop/ABBA/kingswood/masters_delivery, ready for owner's Drive upload. Open before build: releases decision, Drive share link.
- 2026-08-19: Evaluative pass run on the 121 (contact sheets + full-res floor checks). Set opinion delivered in session; internal review gallery published (private artifact). Files at ~/Abba_Photo/kwood819; img/ tiers ingested locally, NOT committed (faces, releases open).
- 2026-08-18: Delivery scaffold built ahead of Aug 23: build_delivery.py (ingest/build/zip, hard RELEASES GATE per the line above), delivery.template.html, process_masters.sh (EXIF strip+stack per the skill), DELIVERY_RUNBOOK.md. Pipeline smoke-tested end to end with dummy frames and cleaned. Nothing live changed; delivery.html does not exist until delivery day.
- 2026-08-08 (on site, Noah dictating, day three, fourth pass): THE GUIDE IS A STARTING
  MANUAL, standalone, "no connection to my being there." Every residency dependency came
  off: the intro paragraphs about what the page is are DELETED on Noah's explicit
  instruction (the guide is a guide and does not introduce itself), the old page-meta
  section 13 is deleted (email moved to the footer), section counts drop to 12. The page
  now OPENS with Noah's direction, his words kept: capture campers engaged in program,
  ideally in good light; indulge campers when they ask for a photo, but do not ask
  permission, it's the job; variety of angles and focal lengths, campers in context and
  happy faces. The permission rule in the pose callout upgraded to this fuller version.
  CAMPANION NAMED as the tracking tool in the midday engine (upload, Campanion tags
  campers, list of who is not yet photographed). Division-of-labor section rewritten
  around the team itself, with visitors as the occasional case. Canon/Nikon translated
  inline where controls diverge: Auto ISO menu names for both, exposure compensation
  location on both bodies, Tv/S and Av/A dual naming in the quick reference and the rule
  line. Night section evergreen (any team member can run it). Main page's media-team
  paragraph updated to the starting-manual framing.
- 2026-08-08 (on site, Noah dictating, day three, third pass): FLEET CORRECTION. The Rebel
  and the Nikon teaching body (D3500) were SOLD, and there are two EF 70-300 zooms in the
  kit. Team page updated: teaching-bodies block removed (with its charger to-do and the
  focus-motor note), the 70-300s join the rigs section (daylight reach on the 5D Mark IV,
  second copy is the backup), run-sheet roles rewritten for two rigs (150 keepers each,
  CITs shadow onto a rig for a block, which is how the shadowing program meets the bar),
  the rounding-out list re-cut (AAA batteries and a card return the trip cameras; the only
  candidate purchase left this summer is the Canon EF 50mm f/1.8 STM so both rigs can work
  an evening room; the Nikon fifty is withdrawn), and the 2027 fifty item is now Canon
  only. Inventory CSV (local): both bodies marked SOLD, the two 70-300s added, the Nikon
  fifty suggestion withdrawn. Open question routed privately: what do CITs shoot on now.
- 2026-08-08 (on site, Noah dictating, day three, second pass): THE REAL RIGS ARE ON THE
  PAGE. Working glass named by Noah: 5D Mark IV with the 24-105 f/4, D850 with the 24-70
  f/2.8 VR and the 70-200 f/2.8 VR (both pro zooms share the one Nikon body; the swap is
  the cost), plus one excellent Manfrotto tripod. Kit section rewritten rig by rig with
  what each is for; the fifty recommendation re-aimed at the TEACHING bodies since the
  working rigs carry fast glass; the open block narrows to teaching-body glass. Run sheet
  updated to Noah's operating design: MORNING DIVIDES BY CAMP SECTION (one shooter owns
  each, trade daily), MIDDAY IS THE ENGINE (upload the morning, tag faces, generate the
  list of campers present and not yet photographed), AFTERNOON SHOOTS THAT LIST IN GOOD
  LIGHT. The numbers section names coverage as the second number next to the 300. New rule
  line in the pose callout, Noah's words kept intact: candid comes first, "do not ask
  permission unless it makes for a better photo." Inventory CSV (local, never in this
  repo) gains the three lenses and the tripod.
- 2026-08-08 (on site, Noah's direction, day three): THE GUIDE HAS A NEW BAR, set by Noah:
  team.html must be something camp can hand a media team and get 300 usable photos a day.
  The page restructured from a craft guide into an operating manual, now 13 sections: new
  02 "The day" (the run sheet: block-by-block keeper quotas summing to 300), new 03 "The
  numbers" (300 kept means roughly 900 shot at a one-in-three keep rate; per-shooter split;
  the daily tally stays public inside the team), new 04 "Before dinner" (same-day sort,
  absorbs the old After-the-shot section; no card rolls over). Kit section gains "Rounding
  out the kit for 300 a day" (returns-to-service first, the two free facts, a fifty per
  photographer, consumables, and what is NOT needed; no money amounts, prices stay
  private). Night sky section rewritten evergreen (first run Thursday night, kept so a
  future team can run it) and moved to sit with the craft sections. CORRECTION from Noah:
  HAVDALAH AT KINGSWOOD IS BEFORE SUNDOWN, so it is a golden-hour ceremony, not a low-light
  one; team page section 07 and the main page's Saturday line both fixed. Main page rolled
  to Saturday (day three): Shabbat through the day, Havdalah before sundown, last working
  night after dark; sky refreshed (storms easing by 8pm, partly cloudy night). The UHD
  video builder Noah asked about is planned and PARKED until after the residency.
- 2026-08-07 (via the morning interview, cloud session, merged here midday): Deliverables
  scope SETTLED with Jodi on day two, and the night sky session RAN. The page's "Where
  things stand" now says the deliverables are settled; the working-shape hedge language is
  retired. The book's emphasis directive is recorded in the private repo, not here. Tour
  specifics (the three buildings for the virtual-tour attempt, the must-capture list) are
  still unrelayed.
- 2026-08-07 (on site, Noah dictating, day two): PAGE MADE VERY CONCISE on Noah's direct
  instruction ("client page needs to be very concise"). The page dropped from fourteen
  sections to nine: open items became a three-line "Where things stand" (shots banked;
  the dedicated book has clear direction from Jodi; media team underway), the five
  fills-in-later deliverable sections merged into one "What lands next" list, the
  Thursday night-session band came off as past (its outcome is NOT yet reported; do not
  claim it ran), the walk paragraph and the Interlaken field-guide reference came off,
  and the sky board compressed to three one-line rows on a fresh NWS pull (Saturday now
  60% storms day and evening, clearing before 3am). NEW TOP: today's focus, Friday, as
  Noah set it: camp scenes with the activities in them, Shabbat preparation, Kabbalat
  Shabbat, the evening dance program in the old rec hall. Status per Noah: good number
  of shots banked, on track to add more for the dedicated book and curate the take with
  clear direction from Jodi (the Thursday 3:00 tour happened; its specifics are not yet
  relayed, so the agreement/scope signature state is UNCHANGED here: sent, not signed).
  "Why I do this" kept untouched: Noah's canon. The book's recipients stay unnamed on
  every public surface, as always.
- 2026-08-06 (on site, from Alex): Gear inventory received (partial, per Noah). Two full-frame bodies in service (Nikon D850 with ADS, Canon 5D Mark IV with KC), two entry DSLRs for CITs and shadows (Nikon D3500 OUT OF SERVICE awaiting a battery charger; a Canon Rebel of unconfirmed model), two AAA point-and-shoots for trips, one missing an SD card. NO LENSES LISTED ANYWHERE, which is the finding. Team page section 08 filled in from the real bodies: what each is for, the D850's file size as the shared cause of slow editing and a filling drive, the D3500's lack of an in-body focus motor (AF-S or AF-P only), and the cheap items that return three cameras to service; the lens list stays an open block until it exists. A rebuilt 17-column inventory sheet was delivered to Noah at ~/Desktop/ABBA/kingswood/inventory/ and deliberately NOT committed to this public repo, because asset lists, serial numbers, and replacement values do not belong on a public URL. The purchase review (their Z8 suggestion, glass before bodies, the two-mount tax) is private, at dashboard docs/KINGSWOOD_MEDIA_TEAM.md, and goes to Alex rather than into the room with Jodi.
- 2026-08-06 (on site, Noah): Noah's read on the team, recorded because it changes what the residency leaves behind: Alex's document is a real working document and Alex is an enthusiastic participant, which is not true of every engagement. Team page gains section 10, "What would make next summer easier": four 2027 recommendations in spending order. FIRST IS A RISK, NOT A PURCHASE: camp's photo archive lives on ONE hard drive with no redundancy, so cloud storage for the offsite third copy leads the list. Then an editing machine at 32GB RAM minimum, then a 50mm f/1.8 (Nikon or Canon to match the bodies, one per photographer, the cheapest lens either maker sells and what makes the dining hall, evening programs, and Havdalah shootable without flash), then the archive organized and closed each summer on the team's own conventions. The main page points at the section and names the single-drive risk plainly. No money amounts anywhere; the business read stays in the private repo.
- 2026-08-06 (on site, from Alex): Alex shoots P mode with manual ISO, and she handed Noah the team's own CIT shadowing document (her document, Session II), which she described as "what we actually do" as opposed to what was outlined: it is a record of the department's live practice, not a plan. ( A leads technical/workflow/Lightroom/organisation, C leads sports and action). Team page gains section 07, "Modes, and when to leave the one you are in", written from P outward: ISO buys shutter speed, watch the shutter number, program shift, then Av, Tv as the sports mode, M for unchanging light and the night sky, plus callouts for Auto ISO with a 1/250 shutter floor and the exposure compensation button. Quick reference and the first-session agenda updated to match; a new intro line says this page sits alongside the training the team already runs and defers to it. THEIR CURRICULUM IS NOT REPRODUCED HERE OR ON ANY PUBLIC PAGE: the read, the integration map, and the gaps worth raising live in the private repo at docs/KINGSWOOD_MEDIA_TEAM.md. Key finding recorded there: their program defers flash and does not cover night (the residency's gap to fill), and Alex already teaches folder structure, naming, and Bridge tagging, so the Aug 30 media-library handback should be built WITH her rather than delivered over her.
- 2026-08-06 (on site, Noah dictating): Media team UNDERWAY: met with Alex. First open session is TONIGHT, night sky photography, 10:00 to 11:15, open to any staff member and not only the photographers. Page changes: the media-team open item now reads underway (scope stays the one open item); a "Tonight: night sky photography" band sits above Last June; the Thursday day-rail line names the session; the media-team section leads with Alex and with sessions being open to all staff. `team.html` gains section 02 (id="night"): why this hour (moonrise 11:33pm, so the session sits in the dark), cloud does not cancel it, what to bring, and the full manual settings written down so staff keep them after tonight, phones included. Sky section rebuilt on a fresh NWS pull, Wednesday card dropped as past; MOON ILLUMINATION WAS WRONG (shifted one night: Thu read 49%, actually 38%; Fri 27%, Sat 17%, Sun 9%) and is corrected. Meeting spot for tonight is named at dinner, not on the page.
- 2026-08-05 (afternoon, Noah dictating): The top of the page is now "First, the open items" and carries TWO: agreement on scope, and thirty minutes with the media team. New page `team.html` (live at /camp-kingswood/team.html, noindex, linked from the top section and from the media-team section): the team's working hub AND their guide, one page doing both. It ships with the craft that holds anywhere (faces first, the windows, frame and sharpness, the focus-point move, sorting and same-day flags, Shabbat/Havdalah low light) and carries dashed open blocks for what gets written after the first session: their kit, their windows off the camp schedule, the daily target. Modeled on the Interlaken field guide, which stays linked from the main page as the finished shape. Sky section refreshed (fog forming late Wednesday night).
- 2026-08-05 (midday): Jodi opened the deliverables by TEXT this morning; Noah replied by text and relayed the exchange (screenshot; full capture in the private repo). Public-safe substance: she confirmed the visit ("I'm in for you coming today"); ONE dedicated book, no second sales book; she wants more usable images and raised an ONLINE INTERACTIVE TOUR as a deliverable idea; Noah reframed: photos first, layouts standard, use guide like Ramah, prints = client demand + quality control, focus/gaps to be discussed on site. Page updated: deliverables section now the literal top; Shabbat (Friday evening) and Havdalah (Saturday night) named on the day rail; "The books" became "The book" (dedicated set, second layout only if useful). JPEGgy deliverables draft updated to match the texts.
- 2026-08-05: THE ASSISTANT HAS A NAME (Noah): client-facing assistant communications for this engagement sign as "JPEGgy, Abba Photo's assistant, for Noah Gallagher", plainly identified as the assistant, never as Noah. First use: the deliverables check-off reply on the "Noah at Kingswood" thread (draft r2899353112457027588, to Jodi cc the assistant), which supersedes the earlier Noah-voice draft (Noah trashes "Before I drive up: the deliverables"). It also tells the camp that replies to noah@abba-photo.com reach both Noah and the assistant during night-work hours. Send-grant sends during Aug 5-10 may sign as JPEGgy.
- 2026-08-05 (pre-departure, Noah dictating): "Last June" band added to the page: five of Noah's June 2025 Kingswood frames (Milky Way dock, the lit sign, moonlit docks, rowboat under stars, sunset), place-only, no faces, processed per the photo-web-processing skill (source: Drive June2025/kwood(hi-res)692025). "The sky over the weekend" section added: per-day full weather + overnight sky + moonrise/illumination + the new-moon note (Aug 12); MANUAL REFRESH ONLY, by hand in live sessions (stamp says as-of; sweeps stay paused). Deliverables moved to the top as an open conversation; the library count came off the page while they settle. Deliverables check-off email STAGED to Jodi cc assistant (draft r-2709146988948061084). Noah's own status: gear packed, cards cleared, batteries charged; personal packing open.
- 2026-08-04: Dates correction SENT to the client (Aug 5-9, Wednesday arrival). Her auto-reply
  says she is unplugged during camp days and names her assistant as the direct contact; that
  assistant is the send-grant designee (addresses in the private contacts file). Sky read for the
  residency pulled: the two clearest nights are Wednesday and Thursday; Friday and Saturday trend
  to storms.
- 2026-08-03: Dates settled Aug 5-9 (Wednesday-night arrival); day rail rebuilt; send-grant window now Aug 5-10.
- 2026-08-03: Arrival corrected to Thursday night Aug 6; the page now carries the full residency shape with Thursday as the first working night.
- 2026-08-03: Hub launched: the weekend plan, deliverables, media-team framing,
  the walk, intake line. No images yet; none shot.
