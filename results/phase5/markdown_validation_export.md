# Condition A validation reports: hand labels vs checker output

For spot-checking. Hand label = what the report text asserts ("unclear" when ambiguous). Checker = `src/report/markdown_claims.py`. Surgeon = SurgWound expert label (None = Uncertain). Each report is shown in full as the VLM wrote it.


---

## 20.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | present | yes |
| edema | unclear | present | absent | n/a |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | not_healed | not_healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Image context:** [caption text redacted]. Parts of the image are blurred or edited, which limits the assessment.

---

### 1. Wound Location
- **Anterior neck**, with a **transverse (horizontal) incision** in the lower cervical region.
- The location and orientation are consistent with a **thyroidectomy, parathyroidectomy, or similar anterior neck procedure** (e.g., a Kocher-type collar incision).
- Estimated visible length is about 6–8 cm.

### 2. Wound Status
- **Healing stage:** Late inflammatory to early proliferative phase, which is appropriate for postoperative day 12.
- **Edge approximation:** The edges appear **well approximated** along the visible length, with no gaping or dehiscence.
- **Incision line:** A thin, dark linear line runs along the incision. This most likely represents **dried blood or a fine eschar/scab**, and possibly residual surgical skin marker. There is no evidence of an open or separated segment.
- **Surrounding skin:** Intact with no blistering, maceration, or skin tears under the device adhesive.

### 3. Closure Method
- **Non-invasive zip-type skin closure device.** The "Stryker" branding is consistent with the **Zip® Surgical Skin Closure system**.
- **Features observed:**
  - Transparent adhesive panels on both sides of the incision.
  - Multiple paired ratcheting straps (about 8–9 visible) crossing the incision and holding the edges together.
- **Advantages:** No needle punctures, a lower risk of "railroad track" scarring, and pain-free removal.
- **Note:** These devices are typically removed around days 7–14. At day 12, **removal is likely due or imminent** and should follow the surgeon's instructions.

### 4. Exudate Characteristics
- **Amount:** None to minimal visible.
- **Type:** No purulent, serous, or serosanguinous drainage is apparent. The dark material along the line appears to be **dried old blood**, not active drainage.
- **Odor:** Cannot be assessed from an image.

### 5. Erythema
- **Mild, diffuse pink discoloration** of the surrounding neck skin.
- Some faint redness near the incision margins and under the adhesive, likely from **normal healing and/or mild adhesive-related irritation**.
- No well-defined spreading cellulitic border or streaking is seen.
- **Limitation:** Image filters and color editing make an accurate erythema assessment difficult.

### 6. Edema
- **Mild or no visible swelling.** The tissue along the incision appears slightly raised, consistent with normal postoperative healing ridge formation.
- No significant localized swelling suggesting a hematoma or seroma.

### 7. Urgency Level
**🟢 LOW / Non-urgent (routine follow-up)**
- The wound appears to be healing as expected for postoperative day 12.
- **Recommended action:** Attend a scheduled follow-up for **device removal and wound check**.

### 8. Infection Risk Assessment
**Overall risk: LOW**

| Factor | Observation | Risk Contribution |
|---|---|---|
| Edge approximation | Intact | Low |
| Purulent drainage | Absent | Low |
| Spreading erythema | Not evident | Low |
| Swelling/fluctuance | Not evident | Low |
| Body site | Neck (well-vascularized) | Low |
| Closure type | Non-penetrating device | Low |
| Adhesive irritation | Possible mild | Minor (monitor) |

### Warning Signs That Need Prompt Medical Attention
- Increasing redness, warmth, or redness spreading beyond the incision
- Pus, cloudy, or foul-smelling drainage
- Fever above 38°C (100.4°F) or chills
- Wound separation after device removal
- **Neck-specific red flags:** rapidly increasing neck swelling, difficulty breathing or swallowing, or voice changes. These may indicate a **hematoma** and require **emergency evaluation**.
- After thyroid or parathyroid surgery: tingling or numbness around the lips or fingertips, or muscle cramps, which can signal low calcium.

### Care Recommendations
1. Keep the area clean and dry, and follow the surgeon's showering guidance.
2. Do not pull at or adjust the zip device. It should be removed by the care team or per instructions.
3. After removal, scar care such as silicone gel or sheets and strict sun protection can begin once the wound has fully closed (usually from weeks 2–3, per the surgeon's advice).
4. Avoid strenuous neck movement or heavy lifting as instructed.

---

**Summary:** This is a transverse anterior neck incision on postoperative day 12, closed with a Stryker Zip non-invasive closure device. It shows good edge approximation, no visible exudate, mild surrounding pinkness, and no significant edema. Healing appears normal, and infection risk is low.

*Disclaimer: This assessment is based solely on a single edited image and does not replace an in-person evaluation by a qualified healthcare provider.*

</details>


---

## 61.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | present | present | present | yes |
| infection | low | low | low | yes |
| exudate | non_purulent | non_purulent | none | yes |
| healing | not_healed | not_healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

*This assessment is based only on a single photograph and is not a substitute for in-person evaluation by a clinician.*

---

### 1. Wound Location
- **Site:** Extremity. Limb contour and hair distribution suggest the **forearm (volar/ulnar aspect)** or possibly the **lower leg**. The exact anatomical site cannot be confirmed from the image.
- **Orientation:** Linear, longitudinal incision running along the long axis of the limb.
- **Estimated length:** About 10–12 cm, based on suture count and spacing.

### 2. Wound Status
- **Type:** Clean, linear surgical incision with primary-intention healing.
- **Healing phase:** Likely early postoperative, in the **inflammatory to early proliferative phase** (roughly days 3–10).
- **Edge approximation:** Generally **well approximated** along most of the length.
- **Focal concern:** There is a short segment near the center-right with a **dark red linear area**. This most likely represents dried blood or clot within the incision line, but **mild superficial edge separation cannot be excluded**.
- **Surface:** Thin dried crust and scab along the incision line. Whitish, flaky material at the left (distal/proximal) end, consistent with dried exudate, residual ointment, or mild skin maceration.

### 3. Closure Method
- **Technique:** **Simple interrupted sutures**, with about 13–14 stitches visible.
- **Material:** Dark-colored non-absorbable suture, likely nylon or polypropylene.
- **Spacing:** Fairly uniform, roughly 0.7–1 cm apart.
- **Suture tension:** Mostly appropriate. The puncture points show mild reddish-brown discoloration, which may reflect normal early healing, minor bleeding, or mild suture-track inflammation.

### 4. Exudate Characteristics
- **Amount:** Minimal to none actively visible.
- **Type:** Dried **serosanguineous** residue and crust along the incision line.
- **Purulence:** **No visible purulent (yellow/green) discharge.**
- **Odor:** Cannot be assessed from the image.

### 5. Erythema
- **Present, mild and localized.** There is a faint pink-red blush immediately around the suture puncture sites and the incision line, extending only a few millimeters.
- **No spreading erythema** or streaking (lymphangitis) is visible.
- This degree of redness is **consistent with a normal inflammatory healing response**.

### 6. Edema
- **Mild periwound swelling** may be present. The skin along the incision appears slightly raised, with subtle puckering at the suture lines.
- **No significant tense or diffuse limb edema** is apparent.

### 7. Urgency Level
- **Low (routine follow-up).**
- No signs requiring emergency intervention, such as dehiscence with exposed tissue, active bleeding, abscess, or necrosis.
- **Recommend:** Routine wound check, and closer inspection of the central segment to confirm the edges remain intact.

### 8. Infection Risk Assessment
- **Current risk: Low to Low-Moderate.**

| Factor | Finding | Risk Contribution |
|---|---|---|
| Purulent drainage | Absent | Low |
| Spreading erythema | Absent | Low |
| Edema | Mild, localized | Low |
| Edge integrity | Mostly intact; possible focal gap or clot | Mild ↑ |
| Suture-site inflammation | Mild redness at puncture points | Mild ↑ |
| Moisture/maceration at one end | Possible | Mild ↑ |

**Overall:** The wound appears to be healing appropriately, with no definitive clinical signs of surgical site infection.

---

### Recommendations
1. **Keep the wound clean and dry.** Gently clean the crust and the macerated end, then apply a dry, breathable dressing.
2. **Monitor daily for warning signs:**
   - Increasing redness, warmth, or redness spreading more than 1–2 cm beyond the incision
   - Worsening pain or swelling
   - Pus or foul odor
   - Fever or chills
   - Widening of the incision gap
3. **Inspect the central segment** to confirm it is clot rather than dehiscence. If the edges are separating, seek clinical review.
4. **Suture removal:** Typically **10–14 days** after surgery for extremities, as directed by the surgeon.
5. **Limit tension on the limb.** Avoid excessive flexion or strain across the incision.
6. **Seek prompt medical attention** if any infection or dehiscence signs develop.

</details>


---

## 76.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | present | yes |
| edema | present | present | present | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | not_healed | not_healed | not_healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based on a single photograph and is for informational purposes only. It does not replace in-person evaluation by a qualified clinician. Lighting, image resolution, and camera angle limit how accurately color, temperature, swelling, and drainage can be judged.

---

## 1. Wound Location
- **Site:** Lateral aspect of the right ankle, over the distal fibula and lateral malleolus region.
- **Orientation:** A longitudinal (vertical) linear incision running roughly parallel to the fibula, extending from just above the lateral malleolus toward the hindfoot.
- **Estimated length:** About 6–8 cm, estimated from surrounding anatomy.
- **Probable procedure context:** The location and pattern are typical of an open reduction and internal fixation (ORIF) for a lateral malleolus or distal fibula fracture, or of lateral ligament reconstruction. This should be confirmed against the surgical record.

## 2. Wound Status
- **Healing phase:** Appears to be early postoperative, likely in the inflammatory or early proliferative phase (roughly days 5–14), with sutures still in place.
- **Edge approximation:** The wound edges appear well approximated along the full length, with no visible gaping, dehiscence, or step-off.
- **Incision line:** Clean, with no obvious necrosis, eschar, or blistering along the incision.
- **Surrounding skin:** The skin appears intact. There is significant ecchymosis (bruising) in the following areas:
  - **Peri-incisional and hindfoot:** Purplish-brown discoloration around the incision, the lateral heel, and the hindfoot.
  - **Lower leg (distal-to-mid shin):** A large, irregular purple-violaceous bruise with yellowish-green margins. The mixed coloration suggests a resolving hematoma several days old. This is consistent with gravity-dependent tracking of blood from the surgical or injury site, or from the original trauma.

## 3. Closure Method
- **Technique:** Simple interrupted sutures.
- **Material:** Dark, likely non-absorbable monofilament (e.g., nylon/Ethilon or polypropylene).
- **Number:** Approximately 10–12 sutures, evenly spaced.
- **Suture condition:** The sutures appear intact and appropriately tensioned. There are no obvious signs of sutures cutting through tissue or of "railroad track" marks at this stage.
- **Expected removal:** Typically 10–14 days post-op for the ankle and foot. This region is prone to slower healing because of thin soft tissue and dependent position.

## 4. Exudate Characteristics
- **Amount:** None visible.
- **Type:** No serous, serosanguineous, or purulent drainage is apparent.
- **Odor:** Cannot be assessed from the image.
- **Dressing:** The wound is currently uncovered. No dressing is available to assess for strike-through.

## 5. Erythema
- **Peri-incisional erythema:** There is no distinct, spreading erythema suggestive of cellulitis. Mild pinkness along the suture line is consistent with normal inflammatory healing.
- **Caveat:** The extensive bruising may mask or mimic erythema. Clinical palpation for warmth and serial observation are needed to distinguish the two.

## 6. Edema
- **Assessment:** Mild to moderate soft-tissue swelling of the ankle and hindfoot appears likely, with some loss of normal malleolar contour.
- **Interpretation:** This is consistent with expected postoperative edema after ankle surgery. Swelling of this degree is common and typically improves with elevation, compression, and time.
- **Note:** Pitting, tenseness, and comparison with the contralateral limb cannot be assessed from the image.

## 7. Urgency Level
**Classification: Low / Routine (non-urgent)**

- The wound appears to be healing as expected, with well-approximated edges and no signs of active infection or dehiscence.
- The bruising, though visually striking, is a common and generally benign finding after ankle fracture surgery.
- **Recommended action:** Continue standard postoperative care and keep the scheduled follow-up for suture removal and wound check.

## 8. Infection Risk Assessment
**Current risk: Low**

| Factor | Observation | Risk Implication |
|---|---|---|
| Wound edges | Well approximated | Favorable |
| Exudate | None visible | Favorable |
| Erythema | No spreading erythema | Favorable |
| Edema | Mild to moderate, expected | Neutral; monitor |
| Ecchymosis/hematoma | Extensive, resolving | Mild increased risk (hematoma can be a nidus for infection) |
| Anatomic site | Lateral ankle, thin soft-tissue envelope | Moderately elevated baseline risk for wound complications |
| Possible hardware | Likely implant (ORIF) | Increases the consequences if infection develops |

**Patient-specific factors to consider (not assessable from the image):** diabetes, smoking, peripheral vascular disease, obesity, immunosuppression, and whether the fracture was open or closed. Each of these raises the risk of wound complications at the ankle.

---

## Recommendations
1. **Elevation:** Keep the limb elevated above heart level to reduce edema and help the bruising resolve.
2. **Wound care:** Keep the incision clean and dry, and follow the surgeon's instructions on dressings and bathing.
3. **Weight-bearing:** Follow the prescribed weight-bearing restrictions and immobilization (boot or splint).
4. **Follow-up:** Attend the scheduled visit for suture removal and radiographic review, if applicable.
5. **Monitor the bruising:** The leg ecchymosis should gradually fade through green and yellow tones over 1–3 weeks.

### Red Flags: Seek Prompt Medical Attention If Any of These Occur
- Increasing redness, warmth, or red streaks spreading from the incision
- Pus, cloudy, or foul-smelling drainage
- Wound edges separating, or sutures pulling through
- Fever above 38°C (100.4°F) or chills
- Pain that worsens rather than improves
- Calf pain, tenderness, or swelling, or sudden shortness of breath or chest pain. These can signal deep vein thrombosis or pulmonary embolism, which is a particular concern after lower-limb surgery with immobilization.
- Severe swelling with numbness, tingling, or pale or cool toes

---
**Summary:** This is a lateral ankle surgical incision closed with simple interrupted non-absorbable sutures. It appears clean, dry, and well approximated, with no clear signs of infection. Extensive resolving ecchymosis of the hindfoot and lower leg, along with mild to moderate edema, are consistent with expected postoperative findings. Urgency is routine, and infection risk is currently low, with standard monitoring advised.

</details>


---

## 91.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | (none) | none | NO |
| healing | healed | not_healed | healed | NO |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based only on a single photograph and cannot replace an in-person clinical evaluation. Image quality, lighting, and angle limit how reliably subtle findings can be assessed.

---

### 1. Wound Location
- **Region:** Anterior or lateral abdominal wall, likely the lower or flank region based on the visible skin fold and clothing at the edge of the frame.
- **Size and type:** A small incision, roughly 1–2 cm, consistent with a **laparoscopic port site, drain site, or minor surgical incision**.

### 2. Wound Status
- **Healing phase:** Appears to be in the **late proliferative or early remodeling (maturation) phase**.
- **Wound edges:** Fully approximated, with a thin, pale-white linear scar in the center.
- **Surrounding tissue:** A cross- or plus-shaped area of **pink-to-violaceous discoloration** surrounds the scar. This is most consistent with:
  - post-inflammatory hyperpigmentation or erythema of a maturing scar, or
  - residual marks from adhesive closure strips or suture tension.
- **Skin integrity:** No visible dehiscence, open areas, scabbing, or ulceration.

### 3. Closure Method
- **No sutures, staples, or adhesive strips are currently visible.**
- The neat linear scar suggests **primary closure**, possibly with absorbable subcuticular sutures, removed sutures, or tissue adhesive/Steri-Strips.
- The cross-shaped pigmentation pattern may reflect where closure strips or a stitch crossed the incision line.

### 4. Exudate Characteristics
- **Type:** None visible.
- **Amount:** None.
- **Odor:** Cannot be assessed from an image.
- **Assessment:** The wound appears dry and epithelialized.

### 5. Erythema
- **Present but mild and localized.** The discoloration is confined to the immediate peri-incisional area, under about 1 cm from the incision.
- Its dusky pink/purple tone and well-demarcated shape suggest **scar maturation or pigmentation rather than spreading cellulitis**.
- No streaking (lymphangitic spread) is visible.
- Faint pinkish linear marks lower on the abdomen likely represent skin folds, pressure marks, or striae and appear unrelated to the incision.

### 6. Edema
- **No significant edema appreciated.** The surrounding skin appears flat, without obvious swelling, induration, or raised margins.
- Mild induration cannot be ruled out without palpation.

### 7. Urgency Level
**LOW / Routine (non-urgent)**
- No signs requiring emergency or same-day evaluation are visible.
- Routine follow-up per the surgeon's standard postoperative schedule is appropriate.

### 8. Infection Risk Assessment
**Overall risk: LOW**

| Criterion | Finding |
|---|---|
| Purulent drainage | Absent |
| Wound dehiscence | Absent |
| Spreading erythema (>1–2 cm) | Absent |
| Significant swelling/induration | Not apparent |
| Necrosis or eschar | Absent |
| Epithelialization | Complete |

**Seek prompt medical review if any of these develop:**
- Increasing redness, warmth, swelling, or pain at the site
- Any drainage, especially cloudy, yellow/green, or foul-smelling
- Fever ≥38°C (100.4°F) or chills
- Reopening of the wound
- A firm, tender lump beneath the scar (possible abscess, seroma, or hernia at a port site)

---

### Summary and Recommendations
This is a **well-healed small abdominal incision** with mild, localized peri-incisional discoloration most consistent with normal scar maturation or post-inflammatory hyperpigmentation. There is no visible evidence of infection.

**Suggested care:**
1. Keep the area clean and dry, and avoid friction from tight waistbands.
2. Protect the scar from the sun (SPF 30+ or covering) for 6–12 months to reduce lasting hyperpigmentation.
3. Once fully closed, consider silicone gel or sheets and gentle scar massage to improve appearance.
4. The discoloration should gradually fade over several months. If it persists, becomes raised, itchy, or thickened (possible hypertrophic scar or keloid), discuss with the surgeon or a dermatologist.
5. Continue scheduled postoperative follow-up.

</details>


---

## 126.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | healed | healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based solely on a single photograph and is for informational purposes only. It does not replace in-person evaluation by a qualified healthcare provider.

---

### 1. Wound Location
- **Region:** Anterior abdominal wall, lower abdomen. The waistband of the clothing is visible at the top of the image.
- **Number of wounds:** Two small incisions are visible:
  - **Incision A (upper):** Near the waistline, a short horizontal linear incision about 1–1.5 cm long.
  - **Incision B (lower/central):** Lower on the abdominal wall, a short oval incision about 1–1.5 cm long.
- **Likely procedure type:** The size, shape, and spacing suggest **laparoscopic (minimally invasive) port-site incisions**, such as those from a laparoscopic cholecystectomy, appendectomy, or gynecological laparoscopy.

### 2. Wound Status
- **Healing phase:** Late proliferative to early remodeling (maturation) phase.
- **Epithelialization:** Both incisions appear **fully epithelialized and closed**. There is no visible gap, dehiscence, or open tissue.
- **Appearance:** Both scars are pink to reddish-pink, slightly raised or shiny, and flat to minimally elevated. This is consistent with a **maturing scar**, likely several weeks post-operation.
- **Scabbing/crusting:** None visible.

### 3. Closure Method
- No sutures, staples, or adhesive strips are visible.
- The fine, even scar lines suggest **absorbable subcuticular sutures and/or tissue adhesive (skin glue)**, which are standard for laparoscopic port sites. Any external closure materials appear to have been removed or absorbed.

### 4. Exudate Characteristics
- **Type:** None visible.
- **Amount:** None.
- **Odor:** Cannot be assessed from the image.
- **Wound bed:** Dry and intact, with no serous, sanguineous, or purulent drainage.

### 5. Presence of Erythema
- **Localized pinkness/redness** is confined to the scar tissue itself. This is typical of new scar formation (immature scar vascularity).
- There is **no spreading erythema** into the surrounding skin and no streaking.
- There is a faint, mottled pinkish tone on the surrounding abdominal skin. This is likely due to lighting, skin pressure, or normal skin variation rather than cellulitis.

### 6. Presence of Edema
- **No significant edema** is apparent.
- The surrounding skin looks smooth, with no obvious swelling, induration, or tense, shiny skin around the incisions.
- Incision B may be very slightly raised, consistent with normal scar tissue. Palpation would be needed to rule out a subcutaneous nodule, seroma, or suture granuloma.

### 7. Urgency Level
**🟢 Low (non-urgent / routine follow-up)**
- There are no signs requiring emergency or urgent care.
- Routine monitoring and standard post-operative follow-up are appropriate.

### 8. Infection Risk Assessment
**Overall risk: Low**

| Indicator | Finding |
|---|---|
| Purulent discharge | Absent |
| Spreading erythema / cellulitis | Absent |
| Swelling / induration | Not apparent |
| Wound dehiscence | Absent |
| Necrosis / discoloration | Absent |
| Abscess / fluctuance | Not apparent (needs palpation to confirm) |

**Interpretation:** These are well-healed, closed port-site incisions with normal scar maturation. The pink coloration is expected and usually fades to a pale or white scar over 6–18 months.

---

### Recommendations
1. **Scar care:** Silicone gel or sheets may help with scar appearance once the wound is fully closed. Gentle massage can also help.
2. **Sun protection:** Protect the scars from UV exposure to prevent hyperpigmentation.
3. **Avoid friction:** A waistband rubbing against Incision A may cause irritation, so loose-fitting clothing may help.
4. **Monitor for warning signs** and seek medical review if any of the following develop:
   - Increasing redness, warmth, or redness spreading outward
   - New swelling, a firm lump, or a fluctuant (fluid-filled) area
   - Drainage of pus or fluid
   - Fever or chills
   - Worsening pain at the site
   - A bulge at the incision when coughing or straining, which may indicate a port-site hernia
5. **Follow-up:** Attend scheduled post-operative visits. Consult a provider if the scars become thick, raised, itchy, or extend beyond the original incision, which may suggest hypertrophic or keloid scarring.

</details>


---

## 133.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | unclear | present | absent | n/a |
| infection | low | low | low | yes |
| exudate | non_purulent | non_purulent | none | yes |
| healing | not_healed | not_healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Image type:** Clinical photograph (non-standardized, taken in a vehicle under natural light)
**Disclaimer:** This assessment is based solely on a single photograph. It does not replace in-person evaluation by a qualified healthcare provider.

---

## 1. Wound Location
- **Region:** Upper extremity, most consistent with the **posterolateral or lateral upper arm** (proximal to the elbow, distal to the shoulder).
- **Context:** The wound's size and appearance suggest a minor procedure, such as an excisional skin biopsy, lesion or cyst removal, or subdermal implant insertion or removal.

## 2. Wound Status
- **Size:** Small linear incision, estimated at **~1–1.5 cm** long.
- **Orientation:** Roughly vertical, along the long axis of the arm.
- **Edge approximation:** The edges appear **well approximated**, with no visible gaping or dehiscence.
- **Healing phase:** **Early or acute postoperative**, likely within 0–48 hours. The wound looks fresh, and a just-removed dressing (non-woven adhesive pad with absorbent center) is visible.
- **Wound bed:** Not exposed. The incision is closed. There is mild surface irregularity and slight puckering at the suture points, which is expected.

## 3. Closure Method
- **Technique:** **Sutures**, most likely **simple interrupted**, with about 2–3 visible throws across the incision.
- **Material:** Fine-gauge suture. The color is hard to determine because of image resolution and blood staining.
- **Adjuncts:** No visible staples, adhesive strips, or tissue glue.

## 4. Exudate Characteristics
- **Amount:** **Minimal or scant.**
- **Type:** **Sanguineous to serosanguineous.** There is slight dried blood along the incision line and a thin trickle of dried blood extending below the wound.
- **Purulence:** **None observed.** No yellow, green, or cloudy drainage.
- **Dressing:** The visible absorbent pad shows no significant saturation.

## 5. Erythema
- **Present:** Yes, **mild and localized**.
- **Extent:** Limited to a narrow pink-red margin of about 2–4 mm immediately around the incision and suture sites.
- **Interpretation:** Consistent with **normal acute inflammatory response** and suture-related trauma. There is no spreading erythema, streaking (lymphangitis), or dusky discoloration.
- **Other findings:** Scattered small reddish follicular papules on the surrounding skin are likely baseline features (e.g., keratosis pilaris), not wound-related.

## 6. Edema
- **Present:** **Minimal or none apparent.**
- **Observation:** Slight elevation of the wound edges, consistent with expected local tissue reaction. There is no significant swelling, tense or shiny skin, or induration visible.
- **Limitation:** Palpation would be needed to assess induration or fluctuance.

## 7. Urgency Level
**🟢 LOW (routine)**
- No signs requiring urgent or emergency evaluation.
- Recommend **routine follow-up**, typically suture removal at **about 7–14 days** for the upper arm, per the treating clinician's instructions.

## 8. Infection Risk Assessment
**Overall risk: LOW**

| Factor | Finding | Risk contribution |
|---|---|---|
| Wound class | Likely clean (Class I) minor procedure | Low |
| Edge approximation | Good | Low |
| Exudate | Scant, serosanguineous, non-purulent | Low |
| Erythema | Mild, confined to edges | Low (expected) |
| Edema | Minimal | Low |
| Wound size | Small | Low |
| Location | Upper arm (good vascularity, low contamination) | Low |

**Patient-specific factors to consider (not assessable from image):** diabetes, immunosuppression, smoking, obesity, and wound care adherence.

---

## Recommendations
1. Keep the wound **clean and dry** for 24–48 hours, or as instructed. Then gentle cleansing with soap and water is usually acceptable.
2. Apply a **clean, dry dressing** as directed. Avoid soaking (baths, pools) until the sutures are removed.
3. Avoid strenuous use or stretching of the arm that may stress the incision.
4. Attend scheduled **suture removal**.
5. **Seek prompt medical attention if any of the following develop:**
   - Erythema spreading more than 1–2 cm from the incision, or red streaks
   - Increasing pain, warmth, or swelling after 48–72 hours
   - Purulent or foul-smelling drainage
   - Fever (>38 °C / 100.4 °F) or chills
   - Wound edges separating, or sutures breaking loose
   - Persistent bleeding not controlled by gentle pressure

---

**Summary:** A small, sutured, linear surgical incision on the upper arm in the early postoperative phase. Edges are well approximated, exudate is scant and serosanguineous, and erythema is mild and localized, with no significant edema. Findings are consistent with **normal early healing**, **low infection risk**, and **routine** urgency.

</details>


---

## 134.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | present | present | absent | yes |
| infection | elevated | elevated | low | yes |
| exudate | purulent | purulent | none | yes |
| healing | not_healed | not_healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

*Based on visual image review only. This does not replace in-person clinical examination.*

---

### 1. Wound Location
- **Probable site:** Trunk, likely the anterior chest or abdominal wall, judging by the smooth broad skin surface and the gauze dressing at the upper edge of the frame.
- **Distribution:** Three lesions in a roughly linear or diagonal arrangement, with a fourth small dark lesion inferolaterally. A linear pattern raises suspicion that the lesions follow an underlying incision, suture line, or drain/port tract.
- A primary incision is not clearly visible. It may lie under the gauze.

### 2. Wound Status
- **Lesion 1 (largest, upper center):** Raised, dome-shaped, violaceous-red papule/nodule about 5–8 mm, with a central yellow-red punctum. This suggests a small pustule, a suture sinus opening, or a localized stitch abscess.
- **Lesions 2 and 3 (middle left):** Smaller red-purple raised papules (about 3–5 mm). They may be early inflammatory foci or healing punctures.
- **Lesion 4 (lower right):** Small dark brown-black flat or slightly raised lesion. It may be a dried scab or crust, or possibly a pre-existing nevus.
- **Overall phase:** Possible delayed or complicated healing at discrete points. Possible causes include suture granuloma, stitch abscess, or folliculitis near the surgical field.

### 3. Closure Method
- **Not directly visible.** No staples, sutures, or adhesive strips are seen in the frame.
- The punctate lesions in a line suggest **prior percutaneous suture or puncture points**, or reactions to **buried absorbable sutures** (suture extrusion or granuloma).

### 4. Exudate Characteristics
- **Amount:** Minimal or scant. No active drainage or dressing saturation is visible.
- **Type:** The central yellowish punctum on the largest lesion suggests possible **purulent or seropurulent material** collecting under the surface.
- **Odor:** Cannot be assessed from the image.

### 5. Erythema
- **Present, localized.** Violaceous-red discoloration is confined to and immediately around each lesion.
- No obvious spreading erythema or streaking (lymphangitis) is seen in the visible field.

### 6. Edema
- **Mild localized edema.** The lesions are raised and indurated in appearance, the largest one most noticeably.
- No significant diffuse swelling of the surrounding skin is evident.
- Faint yellow-green discoloration around the upper lesion suggests **resolving ecchymosis (bruising)**.

### 7. Urgency Level
**Moderate (non-emergent, but prompt review advised within 24–72 hours).**
- No signs of spreading cellulitis, necrosis, or wound dehiscence are seen.
- The pustular appearance of the main lesion still warrants clinical evaluation.
- **Escalate to urgent care if** any of these develop:
  - Fever
  - Rapidly spreading redness
  - Increasing pain
  - Foul-smelling discharge
  - Wound opening

### 8. Infection Risk Assessment
**Risk: Moderate.**

| Factor | Finding |
|---|---|
| Localized pus or punctum | Suggestive (largest lesion) |
| Localized erythema | Present |
| Induration/edema | Mild, focal |
| Spreading cellulitis | Not seen |
| Systemic signs | Unknown |
| Tissue necrosis | Not seen |

**Differential considerations:**
1. Stitch abscess or suture sinus (most likely if absorbable sutures were used)
2. Suture granuloma or foreign-body reaction
3. Superficial surgical site infection (SSI)
4. Folliculitis or furuncle unrelated to surgery

### Recommendations
- Have the wound inspected by a clinician. They can palpate for fluctuance and check for a retained or extruding suture, which may need removal.
- Take a swab for culture if there is discharge.
- Keep the area clean and dry, and change dressings as directed.
- Avoid squeezing or picking at the lesions.
- Monitor temperature and watch for spreading redness or pain.
- Antibiotics should be decided by a clinician. Topical or oral treatment may be considered if infection is confirmed.
- Have the dark lesion (lesion 4) checked to confirm whether it is a scab or a nevus.

</details>


---

## 241.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | present | yes |
| edema | present | present | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | unclear | (none) | healed | n/a |

<details><summary>Full report</summary>

# Wound Assessment Report

**Important note:** This image does not show a surgical wound. There is no incision, suture line, staples, adhesive strips, or dressing. It shows **multiple small, discrete skin lesions** on the arm. The report below follows the requested format but describes what is actually visible. It is a visual observation only, not a diagnosis.

---

### 1. Wound Location
- **Dorsal hand:** two small lesions, one near the base of the index/middle finger knuckle area and one mid-dorsum.
- **Wrist (dorsal/radial side):** one slightly larger, irregular lesion near the wrist crease.
- **Forearm (dorsal/radial side):** two lesions in the mid-to-distal forearm. The lower one is the largest, about 1–1.5 cm.
- **Distribution:** roughly linear along the arm. This pattern can occur with insect bites (e.g., bed bugs, the "breakfast-lunch-dinner" pattern), contact exposure, or scratching.

### 2. Wound Status
- **Type:** Non-surgical. These are raised, pink-to-red papules and small plaques, not an incision.
- **Skin integrity:** Mostly intact. The wrist lesion looks slightly irregular or textured, possibly from scratching or mild surface disruption.
- **Stage:** Appears to be an active or subacute inflammatory skin reaction.

### 3. Closure Method
- **Not applicable.** No sutures, staples, glue, or closure strips are seen. These lesions do not need closure.

### 4. Exudate Characteristics
- **None visible.** There is no drainage, pus, crusting, or weeping, and no visible pustules or vesicles.

### 5. Erythema
- **Present, localized.** Each lesion has pink-to-red coloration confined to it.
- **No spreading redness** or streaking (lymphangitis) is seen between the lesions or up the arm.

### 6. Edema
- **Mild, localized.** The lesions look slightly raised, consistent with small wheals or papules.
- **No diffuse swelling** of the hand, wrist, or forearm.

### 7. Urgency Level
**Low (non-urgent).** Routine evaluation by a primary care provider or dermatologist is reasonable if the lesions persist, spread, or are very itchy.

**Seek prompt care if any of these occur:**
- Rapidly spreading redness, warmth, or red streaks
- Fever, chills, or feeling unwell
- Pus, increasing pain, or hardening around a lesion
- Facial or lip swelling, trouble breathing, or widespread hives (go to emergency care)
- Lesions that blister, ulcerate, or turn dark

### 8. Infection Risk Assessment
**Current risk: Low.**

- **Against infection:** no pus, no spreading erythema, no marked swelling, mostly intact skin.
- **Risk factors to watch:** scratching can break the skin and allow bacteria in (secondary impetigo or cellulitis). The wrist lesion may already have some surface disruption.

### 9. Possible Explanations (for clinician consideration)
- Insect or arthropod bites (bed bugs, fleas, mosquitoes), suggested by the clustered, linear arrangement on exposed skin
- Papular urticaria or another hypersensitivity reaction
- Contact dermatitis
- Less likely: folliculitis or early localized skin infection

### 10. General Recommendations
- Keep the area clean and avoid scratching. Cold compresses may ease itching.
- Over-the-counter options such as oral antihistamines or a mild topical anti-itch cream may help, after checking with a pharmacist or clinician.
- If bites are suspected, check bedding, mattress seams, and pets for signs of bed bugs or fleas.
- Monitor for the warning signs above, and see a healthcare provider if the lesions do not improve within 1–2 weeks or new ones keep appearing.

---
*This assessment is based only on a photograph and cannot replace an in-person exam. If this is actually a post-surgical site, please share an image of the incision area for an accurate surgical wound assessment.*

</details>


---

## 260.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | absent | absent | absent | yes |
| edema | present | present | absent | yes |
| infection | low | low | low | yes |
| exudate | non_purulent | non_purulent | none | yes |
| healing | not_healed | not_healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Image type:** Clinical photograph, dorsal view of the foot
**Note:** This assessment is based on a single photograph and cannot replace in-person clinical examination.

---

### 1. Wound Location
- **Site:** Dorsum of the forefoot and midfoot.
- **Orientation:** A single longitudinal linear incision, roughly 6–8 cm long, running from near the web space between the 2nd and 3rd toes proximally toward the midfoot.
- **Likely procedure context:** This incision position is consistent with forefoot surgery, such as metatarsal fracture fixation (ORIF), a lesser-ray procedure, Morton's neuroma excision via a dorsal approach, or tendon or soft-tissue repair.

### 2. Wound Status
- **Healing phase:** Appears to be in the late inflammatory or early proliferative phase, likely around 1–3 weeks post-op.
- **Wound edges:** Largely apposed along most of the length, covered by a dark brown-black eschar or crust.
- **Areas of concern:** The distal segment, near the toe web space, shows a narrow linear dark line that may represent a small area of superficial separation or thicker crust. Integrity beneath the crust cannot be confirmed from the image.
- **Surrounding skin:** Extensive dry, flaking, desquamating skin across the dorsum, consistent with prolonged dressing coverage, prior antiseptic use, and lack of moisturization. Yellow-brown staining around the incision is most consistent with residual povidone-iodine rather than tissue change.

### 3. Closure Method
- **Primary closure** by suture is evident from the linear, apposed configuration.
- No obvious external sutures or staples are clearly visible, suggesting either recent suture removal or intradermal/absorbable closure. Residual crust may obscure retained sutures; this should be checked in person.
- No visible adhesive strips.

### 4. Exudate Characteristics
- **Type:** Dried serosanguineous to sanguineous crust along the incision line.
- **Amount:** No active drainage visible; the wound appears dry.
- **Purulence:** No visible pus, yellow-green discharge, or moist slough.
- **Odor:** Cannot be assessed from the image.

### 5. Erythema
- **No significant periwound erythema** is evident. The surrounding skin tone is uniform apart from the iodine staining.
- No spreading redness or lymphangitic streaking is visible toward the ankle.

### 6. Edema
- **Mild diffuse dorsal forefoot swelling may be present**, which is common after foot surgery due to dependent positioning.
- No marked localized swelling, fluctuance, or tense, shiny skin is evident.
- Edema should be confirmed by palpation and comparison with the opposite foot.

### 7. Urgency Level
**Low to moderate (routine follow-up, non-emergent).**
- No signs requiring emergency care are visible.
- Recommend routine review within about 1 week, or sooner if the distal segment shows separation once the crust is examined.

### 8. Infection Risk Assessment
**Overall risk: Low to moderate.**

| Factor | Finding | Risk Contribution |
|---|---|---|
| Erythema | Absent | Low |
| Purulent exudate | Absent | Low |
| Edema | Mild at most | Low |
| Wound edges | Mostly apposed; possible minor distal gap | Moderate |
| Location | Foot (thin dorsal skin, distal circulation, footwear friction, moisture between toes) | Moderate |
| Surrounding skin | Dry, scaling (risk of fissures) | Mild |
| Unknown factors | Diabetes, peripheral vascular disease, smoking, implant hardware | Should be clarified |

**Rationale:** The wound appears clean, dry, and without classic infection signs (redness, heat, pus, increasing swelling). However, foot incisions are inherently higher-risk because of distal blood supply, proximity to the web space, and contamination from footwear. If hardware was implanted, any deep infection would carry greater consequences.

---

### Recommendations
1. **Wound care:** Keep the incision clean and dry. Let the crust separate naturally and do not pick it. Avoid soaking until the wound is fully epithelialized.
2. **Distal segment:** Have a clinician inspect the area near the web space to rule out dehiscence. Keep the interdigital space dry.
3. **Skin care:** Apply a gentle emollient to the dry, peeling skin around the wound, but not on the incision itself, to prevent cracks.
4. **Edema control:** Elevate the foot above heart level when resting, and limit prolonged standing as directed by the surgeon.
5. **Footwear:** Wear loose, protective post-op shoes to avoid pressure or friction on the dorsal incision.
6. **Seek prompt review if any of these occur:**
   - Increasing redness, warmth, or spreading discoloration
   - New drainage, especially cloudy, yellow, green, or foul-smelling
   - Wound edges opening
   - Worsening pain or swelling
   - Fever or chills
   - Red streaks up the foot or leg
7. **Patient-specific:** If the patient has diabetes or vascular disease, closer surveillance is advised.

---
*This report is for informational purposes and should be verified through direct clinical examination by the treating surgeon or wound-care professional.*

</details>


---

## 310.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | absent | absent | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | healed | not_healed | healed | NO |

<details><summary>Full report</summary>

# Wound Assessment Report

**Important note:** This image does not show an obvious acute surgical wound. It shows the lower face (nose, lips, cheek, and jawline). The assessment below describes what is visible. A photo assessment cannot replace an in-person exam by a clinician.

## 1. Wound Location
- **Region:** Left cheek, lateral to the oral commissure, near the lower nasolabial fold.
- **Finding:** A faint, short, linear, slightly indented mark about 1–1.5 cm long, running obliquely downward. It may be a well-healed linear scar, a small healed incision or laceration, or a natural skin crease or fold.

## 2. Wound Status
- **Phase:** Appears fully epithelialized (closed, intact skin surface). This is consistent with the late healing or maturation phase if it is a scar.
- **Integrity:** No visible open areas, separation (dehiscence), scabbing, or granulation tissue.
- **Scar character:** Flat to slightly depressed. The color is close to the surrounding skin, possibly with slight pinkness. No hypertrophic or keloid features are evident.

## 3. Closure Method
- No sutures, staples, adhesive strips, or tissue glue are visible.
- If this is a surgical site, closure appears complete, and any sutures were removed or absorbed. The original closure method cannot be determined from the image.

## 4. Exudate Characteristics
- **Amount:** None visible.
- **Type:** Not applicable (no serous, sanguineous, or purulent drainage).
- **Odor:** Cannot be assessed from the image.

## 5. Erythema
- **At the mark:** No significant erythema. At most there is faint pinkness, which is typical of a maturing scar.
- **Surrounding area:** Mild diffuse pinkness on the upper cheek near the eyeglass frame. This is most likely physiologic flushing, pressure from the glasses, or a lighting effect, not inflammation from a wound.
- No spreading redness or streaking is seen.

## 6. Edema
- No visible localized swelling, puffiness, or contour distortion around the mark.
- Facial contours appear symmetric in the visible area.

## 7. Urgency Level
- **Low / routine.** No signs need urgent or emergency care.
- Routine follow-up is appropriate if this is a known post-surgical site.

## 8. Infection Risk Assessment
- **Current risk: Low.**
- **Supporting factors:** Intact skin, no exudate, no meaningful erythema, no edema, and no signs of abscess or cellulitis.
- **Seek medical review if any of these develop:**
  - Increasing redness, warmth, or swelling
  - Pain or tenderness at the site
  - Drainage (especially cloudy, yellow, or green)
  - Fever or feeling unwell
  - Reopening of the skin

## Recommendations
1. **Scar care (if a healing scar):** Use daily broad-spectrum sunscreen (SPF 30+) to prevent darkening. Silicone gel or sheets may help scar maturation over 2–3 months.
2. Avoid picking at or rubbing the area.
3. If the mark is new or changing (growing, raised, bleeding, or changing color), have a dermatologist or the operating surgeon evaluate it.
4. For an accurate assessment, provide clinical history (procedure type, date of surgery, closure method) and a well-lit, close-up, perpendicular image of the specific site.

**Disclaimer:** This report is based on a single photograph of limited resolution and lighting. It is not a diagnosis. Please consult a qualified healthcare provider for clinical evaluation.

</details>


---

## 315.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | present | yes |
| edema | unclear | present | None | n/a |
| infection | low | low | low | yes |
| exudate | none | non_purulent | none | NO |
| healing | not_healed | not_healed | not_healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Note:** This assessment is based only on a single photograph. It cannot replace an in-person exam by a qualified clinician, who can check temperature, tenderness, induration, drainage, and patient history.

---

### 1. Wound Location
- The wound appears to be on the **neck or upper trunk**, likely the posterior neck/upper back or the anterior lower neck/upper chest, based on the green garment neckline at the bottom of the image.
- The incision is short, about **1.5–2 cm**, and oriented roughly horizontally.
- This size and appearance are typical of a minor excision, such as removal of a sebaceous cyst, lipoma, nevus, or a skin biopsy.

### 2. Wound Status
- The **wound edges appear well approximated** with no visible gaping or dehiscence.
- There is no obvious necrosis, eschar, or open tissue.
- The wound appears to be in the **early healing phase (inflammatory to early proliferative)**, probably a few days after the procedure.
- A small amount of dried material or crust may be present at the suture sites.

### 3. Closure Method
- **Simple interrupted sutures**, about 4 stitches.
- The suture material appears dark (black/blue), consistent with **non-absorbable monofilament such as nylon or polypropylene**.
- The suture ends are left moderately long, and the knots appear intact with no broken or loosened stitches.
- Removal is typically due in **about 5–7 days for the neck** or **10–14 days for the back**, as directed by the treating clinician.

### 4. Exudate Characteristics
- **No significant exudate is visible.**
- There is no evidence of purulent (yellow/green, cloudy) discharge.
- Minimal dried serous or serosanguinous residue may be present at the suture puncture points, which is normal.

### 5. Erythema
- **Present, mild, and localized.** There is a pink-to-red zone around the incision, extending roughly **3–5 mm** beyond the wound edges.
- The redness is concentrated along the incision and around the suture entry points.
- There is no visible streaking (lymphangitic spread) and no widespread redness.
- This pattern is **consistent with a normal postoperative inflammatory response or mild suture reaction**. However, it should be watched for spread.
- A faint pink patch at the lower part of the image (near the collar) appears separate and may be friction or pressure from clothing.

### 6. Edema
- **Mild or minimal.** There may be slight swelling immediately around the incision.
- There is no significant swelling, tense skin, or fluctuance (which would suggest an abscess or hematoma).

### 7. Urgency Level
- **Low (routine follow-up).**
- No urgent or emergency features are visible.
- Continue routine wound care and keep the scheduled suture-removal appointment.

### 8. Infection Risk Assessment
- **Current risk: low to mild.**
- **Reassuring features:** good edge approximation, no pus, no streaking, and redness confined to the wound margins.
- **Features to monitor:** the ring of redness around the sutures. If it widens or intensifies, early surgical site infection or stitch abscess becomes a concern.
- **Contributing factors:** the neck/back area has many sebaceous glands and is exposed to collar friction and sweat, which may slightly raise risk.

---

### Recommendations
1. Keep the wound **clean and dry**. Gently clean as instructed, such as with saline, and apply a thin layer of ointment or a dressing if advised.
2. Avoid friction from tight collars, and avoid scratching or picking at the sutures.
3. Have the sutures removed on schedule, since leaving them in too long increases the risk of suture-track marks and infection.
4. **Seek prompt medical review if any of the following occur:**
   - Redness spreading more than about 1–2 cm from the wound, or red streaks
   - Increasing pain, warmth, swelling, or hardness
   - Pus or cloudy or foul-smelling drainage
   - The wound edges opening
   - Fever (over 38 °C / 100.4 °F) or feeling generally unwell
5. Taking daily photos in the same lighting can help track whether the redness is improving or spreading.

**Overall impression:** This is a sutured minor surgical wound in early healing with mild, localized perisutural erythema. It most likely reflects a normal inflammatory response, with no clear signs of infection at present. Routine follow-up is appropriate.

</details>


---

## 322.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | non_purulent | non_purulent | none | yes |
| healing | not_healed | not_healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Image type:** Clinical photograph, anterior abdominal wall
**Likely procedure context:** Multi-port laparoscopic surgery, with a small midline extraction or periumbilical incision

---

### 1. Wound Location
- **Primary incision:** Vertical midline incision just below the umbilicus, about 3–4 cm long. This is consistent with a specimen extraction site or umbilical port extension.
- **Secondary incisions:** At least 4–5 small (≈0.5–1.5 cm) port-site incisions:
  - Right upper quadrant/flank (superior lateral)
  - Right mid-abdomen (lateral to the umbilicus)
  - Right lower mid-abdomen (the most prominent port site, with a crusted, slightly gaping appearance)
  - Right lower quadrant
  - Possibly a small site in the left lateral abdomen
- **Additional findings:** Scattered pink-red patches across the lower abdomen. These are not at incision sites.

### 2. Wound Status
- **Healing phase:** Early postoperative, likely the inflammatory to early proliferative phase (roughly 3–10 days post-op).
- **Midline incision:** Edges appear approximated, with dark crusting and dried blood along the suture line. No obvious dehiscence.
- **Port sites:** Mostly approximated with crust or scab formation. The right lower-mid port site shows a darker, crusted, slightly irregular appearance. Its edges should be checked for minor separation.
- **Overall:** Healing appears to be progressing without gross complications.

### 3. Closure Method
- **Interrupted sutures** (likely non-absorbable, e.g., nylon or polypropylene). These are visible as multiple transverse stitches across the midline incision and across each port site, giving a "ladder" or hash-mark pattern.
- No staples or adhesive strips are clearly visible.

### 4. Exudate Characteristics
- **Amount:** None to minimal.
- **Type:** Dried serosanguineous or sanguineous crust along the suture lines.
- **No visible purulent drainage**, fresh bleeding, or wet exudate.
- **Odor:** Cannot be assessed from the image.

### 5. Erythema
- **Periwound:** Mild, localized pink-brown discoloration around the midline incision, extending only a few millimeters to about 1 cm. This is consistent with normal postoperative inflammation and possible antiseptic staining.
- **Port sites:** Minimal surrounding erythema.
- **Lower abdomen:** Several patchy, poorly defined pink-red areas away from the incisions. Possible causes:
  - Adhesive or dressing reaction (contact dermatitis or tape injury)
  - Pressure or friction marks
  - Heparin/anticoagulant injection sites or minor bruising
- No spreading cellulitis or streaking is evident.

### 6. Edema
- No significant swelling is visible.
- Possible mild induration around the midline incision, which is typical at this stage. Confirming this requires palpation.

### 7. Urgency Level
**Low (routine follow-up).**
- No signs requiring urgent intervention: no dehiscence, active bleeding, purulence, or spreading cellulitis.
- Suture removal is typically planned at about 7–10 days for abdominal wounds, per surgical protocol.

### 8. Infection Risk Assessment
**Current risk: Low to mild.**

| Factor | Finding |
|---|---|
| Purulent drainage | Absent |
| Spreading erythema (>2 cm) | Absent |
| Warmth/tenderness | Not assessable from image |
| Wound edge separation | Not evident; monitor the right lower port site |
| Edema/induration | Minimal |
| Periumbilical location | Moderately higher baseline infection risk (moisture, bacterial load) |

**Monitoring points:**
- The **umbilical/midline site** carries the highest relative risk, since extraction sites have higher surgical site infection rates.
- The **lower abdominal erythematous patches** should be monitored. If they enlarge, become warm or painful, or blister, assess for cellulitis versus adhesive dermatitis.

---

### Recommendations
1. Keep the incisions clean and dry, and use gentle cleansing per protocol.
2. Monitor daily for increasing redness, warmth, swelling, pain, drainage, or fever above 38 °C.
3. If the lower abdominal patches are due to adhesive, use hypoallergenic dressings or barrier film.
4. Plan suture removal at about 7–10 days post-op, depending on healing and surgeon preference.
5. The patient should seek prompt review if there is purulent discharge, wound opening, rapidly spreading redness, or systemic symptoms.

---
*Disclaimer: This assessment is based only on a photograph and cannot replace in-person clinical examination. Palpation, temperature, pain, patient history, and laboratory findings are needed for a definitive evaluation.*

</details>


---

## 433.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | absent | absent | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | unclear | not_healed | healed | n/a |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based on a single photograph and cannot replace an in-person clinical examination. Lighting, angle, and resolution limit evaluation of subtle findings.

## 1. Wound Location
- **Site:** Lower abdomen, suprapubic region, just above the pubic hairline.
- **Orientation:** Transverse (horizontal) incision, consistent with a **Pfannenstiel-type incision**, which is typically used for cesarean section or gynecologic surgery.
- **Associated findings:**
  - A vertical hyperpigmented band in the midline (**linea nigra**), consistent with recent pregnancy.
  - Faint striae (stretch marks) on the lower abdomen, also consistent with the postpartum state.
  - Mild soft-tissue fullness or overhang above the incision, which is common after pregnancy.

## 2. Wound Status
- The incision appears **closed, with well-approximated edges** along its visible length.
- There is no visible gaping, dehiscence, or separation.
- The scar line appears thin and linear, suggesting **primary intention healing** in the early-to-intermediate healing phase.
- No scabbing, eschar, or open granulation tissue is evident.

## 3. Closure Method
- No external sutures, staples, or adhesive strips are visible.
- The findings suggest either **subcuticular (intradermal) absorbable sutures** or prior removal of staples or sutures.
- Faint marks near the lateral ends may represent previous suture or staple entry points or skin-fold artifacts.

## 4. Exudate Characteristics
- **None visible.** There is no serous, serosanguineous, or purulent drainage.
- No dressing is in place and there is no visible staining on the skin or surrounding fabric.

## 5. Erythema
- **No significant erythema is identified** along the incision line or surrounding skin.
- The skin tone around the wound appears consistent with the adjacent abdominal skin.
- Erythema can be harder to judge in darker skin tones and in photographs. Local warmth and subtle color change should be checked in person.

## 6. Edema
- **No obvious localized edema or induration** at the incision.
- Mild generalized fullness of the lower abdominal soft tissue is present, likely reflecting postpartum body habitus rather than wound-related swelling.
- Palpation would be needed to exclude a subcutaneous fluid collection such as a seroma or hematoma.

## 7. Urgency Level
**Low (routine follow-up).** No features requiring urgent or emergency evaluation are seen.

## 8. Infection Risk Assessment
**Current infection risk: Low.**

| Factor | Finding |
|---|---|
| Wound edge approximation | Intact |
| Exudate/pus | Absent |
| Erythema/cellulitis | Not evident |
| Swelling/induration | Not evident locally |
| Dehiscence | Absent |

**Patient-related risk factors to consider:** These cannot be assessed from the image but should be reviewed clinically:
- Obesity or an abdominal pannus overlapping the incision, which creates a moist environment
- Diabetes or gestational diabetes
- Smoking
- Anemia
- Prolonged labor or rupture of membranes
- Emergency surgery

## Recommendations
1. **Keep the incision clean and dry.** Gently dry the skin fold above the incision after bathing.
2. **Continue routine postoperative or postpartum follow-up.**
3. **Seek prompt medical review** if any of the following develop:
   - Increasing redness, warmth, or spreading discoloration
   - Swelling, hardness, or a fluctuant lump
   - Discharge, especially if cloudy, yellow/green, or foul-smelling
   - Wound opening or separation
   - Fever ≥38 °C (100.4 °F), chills, or worsening pain
4. **Scar care:** Once the wound is fully healed (usually several weeks after surgery), silicone gel or sheets and sun protection may improve the scar's appearance.

**Overall impression:** This appears to be a healing, well-approximated transverse suprapubic surgical incision, most consistent with a post-cesarean Pfannenstiel incision. There are no visible signs of infection or complication.

</details>


---

## 498.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | present | yes |
| edema | present | present | absent | yes |
| infection | elevated | elevated | low | yes |
| exudate | non_purulent | non_purulent | none | yes |
| healing | not_healed | healed | healed | NO |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

## 1. Wound Location
- **Site:** Anterior abdominal wall, **lower midline**, extending vertically toward the suprapubic region (pubic hair visible at the inferior margin).
- **Likely procedure type:** Consistent with a lower midline laparotomy or infraumbilical incision (e.g., gynecologic, colorectal, or general abdominal surgery).

## 2. Wound Status
- **Overall:** The incision appears to be **healing by primary intention** along most of its length. The edges look approximated with a thin, linear scar line in the upper segment.
- **Focal abnormality:** In the lower third there is a **small, punctate, dark red/purple opening or raised lesion** (a few millimeters). This may represent:
  - A small area of **superficial dehiscence**,
  - An early **sinus tract** (e.g., from a stitch reaction or a deeper collection), or
  - A **suture granuloma** or retained suture material.
- **Surrounding skin:** Yellow-brown discoloration along the upper incision, most consistent with **resolving bruising** or residual **antiseptic (povidone-iodine) staining**.

## 3. Closure Method
- No staples, external sutures, or adhesive strips are visible.
- The appearance suggests **primary closure** (sutures or staples) that have already been **removed**, or closure with **subcuticular absorbable sutures**. The focal lesion could relate to a buried suture working its way out ("spitting suture").

## 4. Exudate Characteristics
- **Amount:** Minimal to none visible across most of the wound.
- **At the focal opening:** Possible small amount of **serosanguineous** or dried blood material. No obvious frank purulent (pus) drainage is seen in the image.
- **Odor:** Cannot be assessed from the image.

## 5. Erythema
- **Present, localized:** A pink-red halo surrounds the small opening in the lower incision, roughly under 1–2 cm in diameter.
- No widespread or spreading erythema (cellulitis) is evident along the remaining incision.

## 6. Edema
- **Mild localized swelling** may be present around the focal lesion (it appears slightly raised).
- No significant generalized edema or induration of the surrounding abdominal wall is apparent. Firmness, warmth, and fluctuance require palpation.

## 7. Urgency Level
- **Moderate (non-emergent, but prompt review advised).** The wound should be evaluated by the surgical team or a wound clinician within **24–48 hours**.
- **Escalate urgently** if any of the following occur:
  - Fever or chills
  - Increasing or spreading redness
  - Purulent or foul-smelling drainage
  - Wound separation enlarging, or visible deeper tissue
  - Worsening pain, abdominal distension, or feeling systemically unwell

## 8. Infection Risk Assessment
- **Risk level: Moderate.**
- **Supporting factors:**
  - A focal break in the skin with surrounding erythema
  - Possible sinus or suture reaction
  - Lower abdominal and suprapubic location, where moisture, skin folds, and proximity to the groin raise bacterial load
- **Reassuring factors:**
  - Most of the incision appears well-approximated and healing
  - No obvious pus
  - No extensive cellulitis
  - No large dehiscence
- **Differential:** Superficial surgical site infection (SSI) vs. stitch abscess or suture granuloma vs. minor superficial dehiscence. A deeper fluid collection (seroma or abscess) should be excluded if drainage persists.

## 9. Recommendations
1. **Clinical examination:** Palpate for fluctuance, tenderness, and warmth. Probe the opening gently to check depth or sinus tract, and look for any visible suture material.
2. **If drainage is present:** Send a swab for culture before starting antibiotics. Consider ultrasound if a deeper collection is suspected.
3. **Local care:** Clean with saline, apply a sterile non-adherent dressing, keep the area dry, and change the dressing daily or as directed.
4. **Suture-related cause:** Removal of the exposed or retained suture often resolves the lesion.
5. **Antibiotics:** Only if there are signs of cellulitis or confirmed infection, per clinician judgment.
6. **Monitoring:** Photograph and measure at each review, track temperature, and assess risk factors such as diabetes, obesity, smoking, and immunosuppression.

---
*Disclaimer: This assessment is based solely on a single photograph and cannot replace in-person clinical examination. Findings such as warmth, tenderness, depth, odor, and fluctuance cannot be determined from an image. Please consult the treating surgical team for definitive evaluation.*

</details>


---

## 584.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | present | present | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | unclear | not_healed | healed | n/a |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

## 1. Wound Location
- **Site:** Anterior knee, likely the right knee based on brace orientation.
- **Incision type:** Longitudinal (vertical) midline incision running over the patella from the distal thigh to the proximal tibia.
- **Context:** The patient is wearing a **hinged post-operative knee brace** (range-of-motion brace) with padded condylar supports and straps. This pattern is consistent with procedures such as total knee arthroplasty, patellar fracture fixation, extensor mechanism repair, or other open knee reconstruction.

## 2. Wound Status
- **Healing phase:** The incision appears **closed and well-approximated**, with no visible gaps, dehiscence, or open areas.
- **Appearance:** It presents as a linear, slightly pink-to-red healing line, suggesting the **late inflammatory to early proliferative/remodeling phase**. This is likely several weeks post-op.
- **Discoloration:** Purplish-violet patches along the proximal and distal parts of the incision are most consistent with **resolving ecchymosis (bruising)**, which is common after knee surgery.
- **Skin integrity:** The surrounding skin appears intact, with no blistering, necrosis, or maceration visible.

## 3. Closure Method
- No sutures, staples, or adhesive strips are visible.
- Likely scenarios:
  - **Staples or sutures already removed** (typically at 10–14 days), or
  - **Subcuticular absorbable sutures** and/or tissue adhesive (skin glue).
- The edges appear well-approximated along the full length.

## 4. Exudate Characteristics
- **Amount:** None visible.
- **Type:** No serous, serosanguineous, or purulent drainage is apparent.
- **Dressing:** No dressing is present, which suggests the wound is dry enough for open-air healing.

## 5. Erythema
- **Present, mild and localized.** There is linear pink-red coloration directly along the incision line.
- It does not appear to spread significantly into the surrounding tissue, and there are no red streaks (lymphangitic spread).
- **Interpretation:** This is most consistent with **normal healing-related hyperemia** rather than cellulitis. It should still be monitored for any expansion.

## 6. Edema
- **Mild to moderate periarticular swelling** is suggested. The knee contour looks somewhat full and rounded.
- This is typical after knee surgery and can persist for weeks to months, especially after arthroplasty.
- No tense, shiny skin is evident that would suggest a severe effusion or hematoma under pressure.

## 7. Urgency Level
**🟢 LOW / ROUTINE.** Continue standard post-operative follow-up with the surgical team or physiotherapy. No signs require emergency evaluation based on this image alone.

## 8. Infection Risk Assessment
**Overall risk: LOW**

| Factor | Finding | Risk Implication |
|---|---|---|
| Wound closure | Intact, approximated | Favorable |
| Drainage | None | Favorable |
| Erythema | Mild, confined to incision | Likely physiological |
| Edema | Mild–moderate, expected post-op | Neutral; monitor |
| Bruising | Resolving ecchymosis | Not infectious |
| Necrosis/dehiscence | Absent | Favorable |

**Note:** For implant surgery such as knee replacement, any deep infection is serious. Vigilance should continue even when superficial healing looks good.

## Recommendations
1. Keep the incision clean and dry. Follow the surgeon's instructions on showering and bathing.
2. Avoid applying lotions or ointments to the incision unless directed.
3. Continue elevation, cryotherapy (ice), and compression as advised to reduce swelling.
4. Wear the brace and follow range-of-motion and physiotherapy instructions.
5. Monitor daily and **seek prompt medical attention** if any of the following occur:
   - Spreading redness, warmth, or red streaks
   - New or increasing drainage, especially cloudy, yellow, green, or foul-smelling
   - Wound edges separating
   - Fever above 38°C (100.4°F) or chills
   - Increasing rather than decreasing pain or swelling
   - Calf pain, swelling, or tenderness, or sudden shortness of breath (possible DVT or PE)

---
*Disclaimer: This assessment is based solely on a single photograph and is for informational purposes only. It does not replace in-person clinical examination by the treating surgeon or healthcare provider, who can assess temperature, tenderness, fluctuance, and patient history.*

</details>


---

## 597.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | non_purulent | none | NO |
| healing | not_healed | not_healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based on a single photograph and cannot replace an in-person exam by a qualified clinician. Findings such as warmth, tenderness, odor, and wound depth cannot be judged from an image.

---

### 1. Wound Location
- A linear surgical incision on what appears to be the **lateral chest wall, axillary region, or medial upper arm**. The patient's hand is supporting the area.
- The incision runs roughly vertically and slightly curved, about 8–12 cm long (estimated).
- A small separate crusted area sits at the upper end of the incision. This may be a drain site, a separate port, or the top of the incision.

### 2. Wound Status
- **Healing phase:** Likely late inflammatory to early proliferative stage, probably 1–3 weeks after surgery.
- The wound edges appear **mostly approximated** along the length.
- There are **multiple dark brown to black dry scabs (eschar)** along the incision line, most prominent at the upper segment and the mid-to-lower portions.
- **Flaky, peeling white skin** surrounds the incision. This is consistent with dry skin, healing epidermis, or residue from adhesive or dressings.
- No obvious wound gaping (dehiscence) is seen, though small superficial gaps under the scabs cannot be excluded.

### 3. Closure Method
- **No visible sutures, staples, or adhesive strips** at the time of the photo.
- The likely scenario is primary closure with sutures or staples that have since been removed, or closure with absorbable subcuticular sutures and/or skin glue.
- Faint, evenly spaced marks along the line may reflect former suture or staple sites.

### 4. Exudate Characteristics
- **No active drainage is visible.** The wound appears dry.
- There is no evidence of pus, cloudy fluid, or fresh bleeding.
- The scabs suggest earlier minor serous or bloody drainage that has dried.

### 5. Erythema (Redness)
- **Present, mild, and localized.** There is pink to purplish-red discoloration along the incision edges, most noticeable around the upper and lower crusted segments.
- The redness appears **confined to within a few millimeters of the wound edge**, with no obvious spreading redness or streaking.
- This pattern is most consistent with normal healing-related inflammation. Some purplish tone may reflect resolving bruising or early scar formation.

### 6. Edema (Swelling)
- **No significant swelling is visible.** The surrounding skin appears flat, without obvious puffiness or tight, shiny skin.
- Mild swelling under the skin cannot be ruled out from a photograph.

### 7. Urgency Level
- **Low (routine follow-up).**
- There are no visible red-flag features such as pus, spreading redness, wound opening, or significant swelling.
- Routine postoperative follow-up is appropriate.

### 8. Infection Risk Assessment
- **Overall risk: Low to mild.**
- **Reassuring features:** dry wound, edges closed, no pus, only mild redness at the edges, no clear swelling.
- **Features to monitor:**
  - Focal redness around the upper and lower crusted segments.
  - Thick scabs, which can occasionally hide small superficial infections or areas of delayed healing.
  - Location: the axillary or chest-wall area has more moisture, friction, and bacteria, which raises infection risk somewhat.

---

### Recommendations
1. **Keep the wound clean and dry.** Gently cleanse with mild soap and water and pat dry.
2. **Do not pick or remove scabs.** Let them separate on their own.
3. **Moisturize the surrounding peeling skin** with a gentle, fragrance-free emollient, avoiding the open or crusted line unless the surgeon advises otherwise.
4. **Reduce friction** with loose clothing and limited strenuous arm movement, as directed by the surgeon.
5. **Seek prompt medical review if any of the following appear:**
   - Spreading or worsening redness, warmth, or increasing pain
   - Pus or cloudy, foul-smelling drainage
   - Wound edges opening
   - Fever above 38 °C (100.4 °F) or chills
   - Increasing swelling or a firm, fluctuant lump (possible seroma, hematoma, or abscess)
6. **Scar care:** Once the wound is fully closed and the scabs have fallen off, silicone gel or sheets and sun protection may help scar appearance.

**Summary:** This is a closed, dry linear surgical incision that appears to be healing normally, with scabs, mild redness at the edges, and no visible signs of infection. Urgency is low, and routine postoperative follow-up is recommended.

</details>


---

## 606.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | healed | healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based on a single photograph and cannot replace an in-person evaluation by a qualified clinician. Lighting, angle, and image resolution limit accuracy.

---

### 1. Wound Location
- **Site:** Extremity, most consistent with the **anterior/volar forearm** or possibly the anterior lower leg, judging by skin contour and hair distribution.
- **Orientation:** Linear, running obliquely (diagonally) across the limb.
- **Approximate length:** Roughly 3–5 cm (estimated; no scale reference in the image).

### 2. Wound Status
- **Healing stage:** **Healed / late proliferative to early remodeling phase.**
- The incision line is **fully closed and epithelialized**, with no visible gaps, dehiscence, or open areas.
- The scar is **pink-violaceous** and slightly raised or flat, typical of an immature scar several weeks after surgery.
- **Perpendicular "cross-hatch" marks** are visible on both sides of the incision, along with a few small red punctate spots. These are consistent with **healing suture tracks or puncture marks** after suture removal.

### 3. Closure Method
- **Likely:** **Interrupted sutures (now removed)**, based on the evenly spaced transverse marks on either side of the incision line.
- No sutures, staples, adhesive strips, or tissue adhesive appear to remain in place.

### 4. Exudate Characteristics
- **Type:** None visible.
- **Amount:** None.
- No serous, sanguineous, or purulent drainage. No crusting, wet areas, or dressing staining.
- The small red dots appear to be **resolving pinpoint marks or tiny scabs** at suture sites, not active bleeding.

### 5. Erythema
- **Peri-incisional erythema:** **Minimal to mild**, limited to the scar itself and the suture tracks.
- The pink-purple color is **consistent with normal scar maturation** (neovascularization).
- **No spreading redness** beyond the immediate wound margins, and no streaking (lymphangitis).

### 6. Edema
- **Not evident.** The surrounding skin appears flat, with normal texture and visible hair follicles.
- No apparent swelling, induration, or tense, shiny skin.

### 7. Urgency Level
- **LOW (routine).**
- No signs requiring urgent or emergency care. Routine follow-up per the surgeon's schedule is appropriate.

### 8. Infection Risk Assessment
- **Current risk: LOW.**

| Indicator | Finding |
|---|---|
| Purulent discharge | Absent |
| Spreading erythema (>1–2 cm) | Absent |
| Edema / induration | Absent |
| Wound dehiscence | Absent |
| Increased warmth / pain | Cannot assess from photo |
| Fever / systemic signs | Cannot assess from photo |

**Overall impression:** A well-healed linear surgical scar after suture closure, with residual suture-track marks and normal scar coloration. No clinical evidence of infection.

---

### Recommendations
1. **Scar care:**
   - Gentle cleansing and daily moisturizing.
   - Silicone gel or sheets may help with scar appearance once the skin is fully closed.
   - Gentle scar massage after about 2–3 weeks post-op, if the surgeon approves.
2. **Sun protection:** Use SPF 30+ or cover the scar for 6–12 months to prevent hyperpigmentation.
3. **Monitor for hypertrophic or keloid scarring:** Watch for progressive thickening, itching, or the scar extending beyond its borders.
4. **Seek medical review if any of the following develop:**
   - New pain, warmth, or swelling
   - Spreading redness
   - Drainage or pus
   - Opening of the wound
   - Fever
5. Expect the color to fade gradually from pink-purple to pale or skin-toned over **6–18 months**.

</details>


---

## 615.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | (none) | absent | NO |
| edema | present | (none) | absent | NO |
| infection | elevated | (none) | low | NO |
| exudate | purulent | (none) | none | NO |
| healing | not_healed | (none) | healed | NO |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Wound Location:**
Trunk, most likely the abdominal wall or flank, based on the hair-bearing skin and its texture. A linear surgical scar runs roughly horizontally from the left side of the image and ends at a focal lesion in the lower-center area.

**Wound Status:**
- The linear part of the incision appears **healed**. It is a mature-to-maturing scar with a violaceous (pink-purple) tone, typical of a scar a few weeks to months old.
- At one end of the scar there is a **focal non-healed area**: a small (a few mm) punctate opening covered by yellow-brown/amber crust or granulation-like tissue.
- The surrounding skin is **puckered and retracted** toward this point, with a slightly shiny, tense appearance. This suggests tethering to deeper tissue.
- Overall picture: **localized wound dehiscence or a sinus tract**. This is most consistent with a **suture sinus or suture granuloma** (a reaction to a buried, non-absorbable or slowly absorbing suture or knot), or possibly a small stitch abscess.

**Closure Method:**
Primary closure. No external sutures or staples remain. The fine linear scar suggests sutured closure, possibly with buried subcuticular or deep sutures. The focal lesion at the end of the incision is a classic site for a buried knot.

**Exudate Characteristics:**
- Scant amount.
- Serous-to-seropurulent, with dried amber/yellow-brown crust at the opening.
- No frank copious purulent drainage is visible.
- Odor cannot be assessed from the image.

**Erythema:**
**Present, mild.** There is faint pinkish erythema around the focal lesion and along parts of the scar, extending a short distance into the surrounding skin. There are no obvious spreading streaks (lymphangitis) and no dusky or necrotic changes.

**Edema:**
**Mild localized swelling/induration** appears around the opening. The skin there looks raised, shiny, and puckered. There is no diffuse edema of the surrounding area.

**Urgency Level:**
**Moderate (non-emergent, but needs clinical review within days).**
- This is not an emergency. There are no signs of necrotizing infection, extensive dehiscence, or systemic involvement visible.
- Seek prompt evaluation sooner if any of the following develop: fever, increasing pain, rapidly spreading redness, increasing purulent drainage, or a fluctuant swelling.

**Infection Risk Assessment:**
**Moderate risk.**
- **Supporting factors:** a persistent focal opening with crusted exudate, localized erythema and induration, and possible retained foreign material (suture). A sinus with a retained suture often does not heal until the material is removed, and it can harbor low-grade infection.
- **Reassuring factors:** the rest of the incision is well healed, the erythema is limited, and there is no apparent abscess, cellulitis, or lymphangitic spread.
- **Differential considerations:** suture sinus or granuloma, superficial stitch abscess, chronic sinus tract to deeper tissue (e.g., a mesh-related or deeper surgical-site infection if prior hernia repair), or hypertrophic scar with focal breakdown.

**Recommendations:**
1. **Clinical examination:** probe the opening to assess depth, check for a palpable or retained suture, and look for fluctuance.
2. **Wound swab culture** if there is purulent drainage.
3. **Remove the offending suture** if one is identified. This is often curative.
4. **Ultrasound** if a deeper collection, sinus tract, or mesh involvement is suspected.
5. **Local wound care:** gentle cleansing and a sterile non-adherent dressing.
6. **Antibiotics** only if there is cellulitis or confirmed infection. They are not routinely needed for a simple suture sinus.
7. **Monitoring:** watch for systemic signs and for the area enlarging or failing to heal.

*Note: This assessment is based on a single photograph and cannot replace in-person examination by a qualified clinician.*

</details>


---

## 625.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | present | yes |
| edema | present | present | present | yes |
| infection | elevated | elevated | low | yes |
| exudate | non_purulent | non_purulent | None | yes |
| healing | not_healed | not_healed | not_healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Image type:** Clinical photograph of a sutured wound
**Note:** This assessment is based only on a single photograph. It cannot replace in-person examination by a clinician.

---

### 1. Wound Location
- **Region:** Lower extremity, foot and ankle.
- **Specific site:** The medial aspect of the foot, just distal and anterior to the medial malleolus (inner ankle), near the midfoot/hindfoot junction.
- **Size:** Roughly 2–3 cm, with an irregular, curved or zigzag (stellate-like) shape. This suggests repair of a traumatic laceration or a small excision rather than a straight planned surgical incision.

### 2. Wound Status
- **Healing phase:** Early postoperative or post-repair, most likely the inflammatory to early proliferative phase (about 2–7 days).
- **Wound edges:** Mostly approximated. There is mild puckering and some edge irregularity along the curved part of the wound.
- **Wound bed and surface:** A dark linear crust or eschar (dried blood/scab) runs along the suture line. No obvious dehiscence (wound reopening), gaping, or exposed deep tissue is visible.
- **Surrounding skin:** Diffuse yellow-orange staining of the foot and ankle, consistent with povidone-iodine (Betadine) antiseptic rather than jaundice or bruising. The skin otherwise looks intact, with no blistering or maceration.

### 3. Closure Method
- **Technique:** Primary closure with simple interrupted sutures.
- **Suture material:** Dark (black/blue) monofilament, most likely nylon or polypropylene (non-absorbable).
- **Number of sutures:** About 6–8 visible.
- **Comments:** Suture tails are cut fairly long. The sutures follow the irregular wound contour. Typical removal time for foot and ankle sutures is **10–14 days**, since healing is slower in this location.

### 4. Exudate Characteristics
- **Amount:** Minimal or scant.
- **Type:** Dried serosanguineous (blood-tinged) material crusted along the incision line.
- **Purulence:** No visible pus, cloudy discharge, or active drainage.
- **Odor:** Cannot be assessed from the image.

### 5. Presence of Erythema
- **Present: Yes, mild to moderate and localized.**
- A pink-red halo extends a few millimeters (about 3–8 mm) around the suture line. It is most noticeable around the central and lower parts of the wound.
- No spreading erythema, streaking (lymphangitis), or poorly defined advancing redness is visible.
- Interpretation: This likely reflects the normal inflammatory response and suture-related reaction. However, it should be watched for spread beyond about 1–2 cm.

### 6. Presence of Edema
- **Present: Mild, localized.**
- There is slight raised swelling of the tissue immediately around the incision.
- Mild generalized fullness of the medial ankle may be present, which is common after foot and ankle injury or surgery due to gravity-dependent swelling.
- No tense or shiny skin suggesting significant swelling or a collection (hematoma or abscess) is evident.

### 7. Urgency Level
**Low to moderate (non-emergent; routine follow-up advised).**
- No signs requiring emergency care are visible, such as purulent discharge, wound reopening, spreading cellulitis, necrosis, or crepitus.
- A routine wound check at the scheduled follow-up, or within 2–3 days if the redness persists, is reasonable.

**Seek prompt medical review if any of these develop:**
- Redness spreading more than 1–2 cm from the wound, or red streaks up the leg
- Increasing pain, warmth, or swelling after the first 48–72 hours
- Pus, cloudy or foul-smelling drainage
- Fever or chills
- Wound edges separating
- Numbness, color change, or coldness of the toes or foot

### 8. Infection Risk Assessment
**Overall risk: Moderate.**

| Factor | Assessment |
|---|---|
| Anatomical site | Foot and ankle wounds carry higher infection risk due to lower blood flow, gravity-dependent swelling, footwear friction, and bacterial colonization of the skin. |
| Wound type | The irregular shape suggests a traumatic laceration, which carries more contamination risk than a clean surgical incision. |
| Local signs | Mild periwound erythema and swelling are present, but no purulence, which is consistent with normal inflammation at this stage. |
| Exudate | Minimal, dried, and non-purulent, which is reassuring. |
| Wound edges | Approximated with no dehiscence, which is reassuring. |
| Unknown factors | Diabetes, peripheral vascular disease, smoking, immunosuppression, and the injury mechanism (e.g., dirty or penetrating object, glass, metal) would significantly change the risk. Tetanus immunization status should also be confirmed. |

**Current impression:** The wound appears to be healing within expected limits, with no clear signs of established surgical site infection. Early superficial infection cannot be fully excluded from a photo, given the redness around the suture line.

---

### Recommendations
1. Keep the wound clean and dry. Follow the clinician's dressing-change instructions.
2. Elevate the foot when resting to reduce swelling.
3. Limit weight-bearing and friction, and avoid tight footwear over the incision.
4. Do not soak the foot (baths, swimming) until the sutures are removed and the wound has closed.
5. Monitor the redness. Marking its border with a pen helps track whether it is spreading.
6. Return for suture removal at about 10–14 days, or as instructed.
7. Patients with diabetes or circulation problems should have a lower threshold for early review.

*This report is for informational purposes only. A definitive assessment requires in-person examination by a qualified healthcare provider.*

</details>


---

## 671.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | absent | absent | absent | yes |
| edema | unclear | present | absent | n/a |
| infection | low | low | low | yes |
| exudate | none | non_purulent | none | NO |
| healing | not_healed | not_healed | not_healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

## 1. Wound Location
Multiple small incisions on the anterior abdomen, consistent with **laparoscopic port sites**:
- **Upper midline (epigastric/subxiphoid) incision:** small, roughly 5–10 mm.
- **Umbilical incision:** at the umbilicus, likely the main camera or extraction port.
- **Lateral abdominal incision:** on the left side of the image (likely the patient's left flank or upper quadrant), about 5–10 mm.

This pattern suggests a procedure such as laparoscopic cholecystectomy, appendectomy, or a similar minimally invasive surgery.

## 2. Wound Status
- All visible incisions appear **well approximated**, with no obvious dehiscence or gaping.
- Edges look aligned. A small amount of dried blood or scab is seen at the incision lines.
- **Ecchymosis (bruising)** surrounds the port sites:
  - Yellow-green bruising around the epigastric and lateral ports.
  - Purplish-blue bruising just below the umbilicus.
- The yellow-green color indicates **resolving bruising**, typical several days after surgery (about days 3–7).
- Overall, healing looks like an **early post-operative, uncomplicated course**.

## 3. Closure Method
- **Sutures** are visible, with small suture knots or ends at the umbilical and lateral port sites.
- The epigastric site likely also has a suture or subcuticular closure, possibly with tissue adhesive.
- No staples are seen.

## 4. Exudate Characteristics
- **No active exudate** is visible.
- There is minimal dried serosanguineous material or crusting at the incision lines, which is normal.
- No purulent (pus-like) drainage is evident.

## 5. Erythema
- **No significant erythema** is seen spreading from the incision margins.
- The faint pink-reddish tone around the periumbilical area appears to be part of the bruising pattern rather than inflammatory redness.
- No streaking (lymphangitis) is seen.

## 6. Edema
- **Mild or minimal localized swelling** may be present around the umbilical port, which is expected after port insertion and specimen extraction.
- No marked induration or tense swelling is seen.

## 7. Urgency Level
**Low (routine follow-up).**
- Findings are consistent with normal post-laparoscopic healing.
- Bruising around port sites is a common, benign finding caused by minor vessel injury during trocar placement.

## 8. Infection Risk Assessment
**Low risk at present.**

| Parameter | Finding | Concern |
|---|---|---|
| Purulent drainage | Absent | No |
| Spreading erythema | Absent | No |
| Warmth or induration | Not apparent visually | Clinical check advised |
| Wound dehiscence | Absent | No |
| Ecchymosis | Present, resolving | Benign |

**Notes:**
- The umbilical site carries a somewhat higher baseline infection risk because of skin folds, moisture, and its frequent use for specimen extraction. It should be kept clean and dry.
- Watch the area of deeper purple bruising below the umbilicus for an enlarging, tender, or fluctuant swelling, which could indicate a **hematoma**.

## Recommendations
1. Keep incisions clean and dry, and pat the umbilical area dry after showering.
2. Monitor for warning signs:
   - Increasing redness, warmth, or pain
   - Pus or foul-smelling discharge
   - Fever above 38°C (100.4°F)
   - An expanding or firm swelling, which may suggest a hematoma or seroma
   - Wound opening
3. Remove sutures or review the wounds at about 7–10 days post-op, if non-absorbable sutures were used.
4. Reassure the patient that the bruising should fade over 1–2 weeks.
5. Have the patient seek prompt evaluation if any of the warning signs develop.

*Disclaimer: This assessment is based only on a photograph. Clinical correlation with an in-person exam, vital signs, and patient symptoms is needed for a definitive evaluation.*

</details>


---

## 688.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | (none) | None | NO |
| healing | healed | healed | healed | yes |

<details><summary>Full report</summary>

# Wound Assessment Report

**Disclaimer:** This is an image-based observational assessment for informational purposes only. It is not a diagnosis and does not replace in-person evaluation by a qualified clinician.

---

### 1. Wound Location
- **Anatomical site:** Anterior upper chest, **presternal / midline sternal region**, below the suprasternal notch and clavicles.
- **Lesions observed:** Three distinct lesions arranged roughly horizontally:
  - A small, raised pink papule-like lesion (upper, near midline)
  - A small elongated raised lesion (middle-left)
  - A larger, horizontally oriented, raised plaque (lower), approximately 2–3× the length of the others

### 2. Wound Status
- **Healing phase:** **Healed / mature to remodeling phase.** There is no open wound, no visible dehiscence, and the epithelium is intact.
- **Morphology:** The lesions are **raised, firm-appearing, shiny, pink-to-flesh-colored scars** with visible **telangiectasias** (fine branching surface blood vessels), particularly on the largest lesion.
- **Impression:** The appearance strongly suggests **hypertrophic scarring or keloid formation.** The presternal chest is one of the most keloid-prone sites in the body. The lesions' slightly irregular borders, which extend modestly beyond a typical linear incision, raise suspicion for **keloid**. Clinical history is needed to distinguish the two, specifically whether the lesions have grown beyond the original wound margins.
- **Surrounding skin:** Normal texture with mild follicular prominence. No maceration.

### 3. Closure Method
- **No sutures, staples, steri-strips, or adhesive present.** The wound is fully closed and epithelialized.
- The original closure method cannot be reliably determined. The scar pattern may reflect a prior excision, a minor procedure, or possibly acne- or trauma-related injury rather than a classic sternotomy, which would typically be a long vertical midline scar.

### 4. Exudate Characteristics
- **Type:** None
- **Amount:** None visible
- **Odor:** Not assessable from the image, but no clinical signs suggest it.
- The surface is dry and intact.

### 5. Erythema
- **Present, localized to the scar tissue itself.** The pink-red coloration and telangiectasia are consistent with **scar vascularity (an active or immature scar)**, not cellulitis.
- **Surrounding skin:** No spreading erythema, streaking, or peri-wound redness.

### 6. Edema
- **No peri-wound edema observed.**
- The elevation of the lesions reflects **excess collagen deposition (scar hypertrophy)**, not fluid swelling.

### 7. Urgency Level
- **Low (non-urgent / routine).**
- No signs of acute complications such as infection, dehiscence, bleeding, or abscess.
- A **routine elective referral to dermatology or plastic surgery** is recommended for scar management, especially if the lesions are symptomatic (itching, pain, tenderness) or enlarging.

### 8. Infection Risk Assessment
- **Current infection risk: Very low.**
  - The epithelium is intact with no portal of entry.
  - There is no purulence, warmth indicators, spreading erythema, or fluctuance.
- **Considerations:**
  - Scratching itchy keloids can cause excoriation and secondary infection.
  - Future procedures or trauma in this area carry a **high risk of keloid recurrence or new keloids**. This is relevant for any planned surgery, piercing, or cosmetic procedure in the region.

---

### Summary and Recommendations
| Parameter | Finding |
|---|---|
| Location | Presternal anterior chest |
| Status | Healed; hypertrophic scar / probable keloid |
| Closure | Fully epithelialized, no closure materials |
| Exudate | None |
| Erythema | Scar-confined vascularity with telangiectasia; no cellulitis |
| Edema | None |
| Urgency | Low / routine |
| Infection risk | Very low |

**Suggested management options for discussion with a clinician:**
- Silicone gel or sheets, used consistently for at least 2–3 months
- Pressure therapy where feasible
- Intralesional corticosteroid injections (e.g., triamcinolone), first-line for keloids
- Pulsed-dye laser for redness and telangiectasia
- Cryotherapy, 5-FU, or combined approaches for resistant lesions
- **Avoid simple surgical excision alone**, as keloid recurrence rates are high without adjuvant therapy.
- Monitor for growth, pain, ulceration, or rapid change, which warrant earlier evaluation.

</details>


---

## 705.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | unclear | present | None | n/a |
| edema | absent | absent | None | yes |
| infection | low | low | low | yes |
| exudate | none | none | None | yes |
| healing | unclear | healed | not_healed | n/a |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Image quality note:** The photo is dim, low-resolution, and taken at close range. A finger at the top of the frame partly obscures the field. These limits reduce confidence, especially in judging color (erythema) and fine surface detail.

---

### 1. Wound Location
- The skin appears to be the **trunk, likely the abdominal wall**, with soft, mobile tissue being pressed or stretched by a finger.
- The lesion's small size and round shape fit a **laparoscopic port site, drain site, or small puncture/stab incision**. A periumbilical location is possible but cannot be confirmed.

### 2. Wound Status
- There is a **small, punctate (~3–5 mm), dark red-brown lesion**, likely a scab or eschar over a healing puncture.
- The edges appear **approximated and closed**, with no visible gaping or dehiscence.
- There is no obvious cavity, tunneling, or exposed deeper tissue.
- **Impression:** The wound appears to be in the **late inflammatory to early proliferative/maturation phase**, healing by primary intention or as a small secondary-intention site.

### 3. Closure Method
- **No sutures, staples, or adhesive strips are visible.**
- The site may have been closed with absorbable subcuticular sutures or tissue adhesive, or left to heal on its own (common for small port or drain sites).
- Any external closure material appears to have been removed or absorbed.

### 4. Exudate Characteristics
- **No active drainage is evident.**
- There is a slight sheen or darker center, which may be dried blood or crust. It does not appear to be purulent or serous discharge.
- Amount: none to minimal (dried).
- Odor: cannot be assessed from an image.

### 5. Erythema
- There is a **faint pinkish/reddish tinge just above the lesion**, possibly localized and less than 1 cm.
- This may be normal healing hyperemia or pressure from the finger. Lighting makes it impossible to judge reliably.
- There is **no spreading or streaking redness** in the visible field.
- **Assessment:** Minimal or no significant erythema.

### 6. Edema
- **No obvious swelling** or raised induration is visible around the site.
- The surrounding skin appears flat and has normal fold patterns.
- **Assessment:** No significant edema.

### 7. Urgency Level
**Low / routine.**
- There are no visible signs of acute complications such as dehiscence, abscess, purulent drainage, or spreading cellulitis.
- Routine follow-up per the surgical team's plan is appropriate.

### 8. Infection Risk Assessment
**Low risk based on visible features.**

| Factor | Finding |
|---|---|
| Purulent discharge | Absent |
| Spreading erythema | Absent |
| Swelling/induration | Absent |
| Wound separation | Absent |
| Eschar/scab | Present (normal healing) |

**Seek prompt medical review if any of the following develop:**
- Increasing redness, warmth, or redness spreading more than 1–2 cm from the site
- Pus, cloudy or foul-smelling drainage
- Increasing pain, tenderness, or a firm lump under the site (possible abscess or port-site hernia)
- Fever above 38 °C (100.4 °F) or chills
- Wound opening

### Recommendations
1. Keep the site clean and dry. Do not pick at the scab and let it separate on its own.
2. Gentle washing with soap and water is usually fine. Avoid soaking (baths, swimming) until it is fully healed, unless the surgeon advises otherwise.
3. For better remote assessment, retake the photo in **bright, natural light** without pressing on the skin, with a ruler or coin for scale and a wider view of the surrounding area.
4. Follow up with the surgical team as scheduled.

---
*Disclaimer: This assessment is based only on a single low-quality image and cannot replace an in-person clinical examination. Any concerning symptoms should be evaluated by a healthcare professional.*

</details>


---

## 740.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | present | present | absent | yes |
| infection | low | low | elevated | yes |
| exudate | purulent | purulent | purulent | yes |
| healing | not_healed | not_healed | not_healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Note:** This is based on a single photograph and is not a substitute for in-person clinical evaluation. Lighting, angle, and gauze coverage limit what can be seen.

---

### 1. Wound Location
- **Likely site:** A skin fold or curved body surface, possibly the lower abdomen, inguinal/groin region, or the area under a fold such as the axilla or inframammary region. The surrounding skin appears to curve into a crease.
- **Surroundings:** Dark linear marks, likely surgical skin marker or residual antiseptic/ink, are visible around the wound. They form intersecting lines consistent with preoperative or procedural markings.
- **Visibility:** Sterile gauze is being retracted by gloveless fingers to expose the site, so only part of the incision is visible.

### 2. Wound Status
- A small, focal area of disrupted or open tissue is visible at the intersection of the marker lines. It appears as a small punctate or short linear opening.
- The tissue in the wound bed looks moist, with **yellow-orange to reddish material**. This may be fibrinous slough, serosanguineous crust, or early granulation tissue.
- The rest of the visible skin along the marked lines appears largely intact. This suggests either a **small incision (e.g., port site, drain site, or minor excision)** or a **localized area of superficial dehiscence**.
- **Healing phase:** Likely early, in the inflammatory or early proliferative phase, based on the moist bed and residual exudate.

### 3. Closure Method
- **No sutures, staples, or adhesive strips are clearly visible** in the image.
- Possible explanations:
  - Subcuticular (buried) absorbable sutures
  - Tissue adhesive (skin glue), which may explain the shiny, crusted appearance
  - A small wound left to heal by **secondary intention** (e.g., a drain site or abscess drainage site)
- Closure method **cannot be confirmed** from this image.

### 4. Exudate Characteristics
- **Amount:** Small/scant. The visible gauze does not appear heavily saturated.
- **Color:** Yellowish-orange with reddish-brown areas.
- **Type:** Most consistent with **serosanguineous to seropurulent** exudate, or a mix of fibrin and dried blood.
- **Consistency:** Appears moist and slightly viscous at the wound center.
- Odor and the exact consistency cannot be assessed from a photo. Frank purulence (thick, opaque, creamy yellow-green) is **not clearly evident**, but cannot be excluded.

### 5. Erythema
- **Mild perilesional redness/pinkness** may be present immediately around the opening.
- **No obvious spreading or extensive erythema** is seen in the visible skin.
- Darker skin tone, lighting, and marker ink limit assessment. Erythema extending more than 1–2 cm from the wound edge would be concerning but cannot be confirmed here.

### 6. Edema
- **Mild localized swelling** may be present, suggested by slight puffiness at the wound site within the skin fold.
- **No marked induration or tense swelling** is apparent.
- Edema is best assessed by palpation, which a photograph cannot replace.

### 7. Urgency Level
**Moderate (non-emergent, but needs timely clinical review within 24–48 hours)**

Rationale:
- There is visible exudate and a possible small area of wound opening.
- There is no obvious extensive dehiscence, necrosis, heavy bleeding, or widespread cellulitis.

**Escalate to urgent or same-day care if any of the following occur:**
- Fever above 38°C (100.4°F), chills, or feeling generally unwell
- Spreading redness, warmth, or red streaks
- Increasing pain, swelling, or hardness
- Thick, foul-smelling, or green/yellow pus
- The wound opening widening, or deeper tissue becoming visible
- Bleeding that soaks through dressings

### 8. Infection Risk Assessment
**Overall risk: Low to Moderate**

| Factor | Observation | Risk Contribution |
|---|---|---|
| Exudate | Yellow/serosanguineous, small amount | Moderate |
| Erythema | Mild, localized at most | Low–Moderate |
| Edema | Mild, if present | Low |
| Wound integrity | Possible small opening or dehiscence | Moderate |
| Location | Skin fold (moisture, friction, bacterial load) | Moderate–High |
| Hand hygiene in image | Bare fingers near the wound | Contamination concern |

**Key concerns:**
- **Skin-fold location** raises infection risk through moisture, maceration, and friction.
- **Yellow exudate** may be normal fibrin, or an early sign of superficial surgical site infection (SSI).
- **Ungloved handling** near the wound raises contamination risk.

### 9. Recommendations
1. **In-person evaluation** by the surgical team or a wound care nurse to palpate for induration, fluctuance, or tenderness and assess odor.
2. **Wound swab for culture** if exudate becomes purulent or increases.
3. **Hygiene:** Wash hands thoroughly and wear clean gloves for dressing changes.
4. **Dressing care:** Keep the site clean and dry. Use a sterile, absorbent dressing and change it as instructed or when soiled or wet. Keep the skin fold dry, for example with an absorbent layer.
5. **Monitor and record:** Daily photos taken in the same lighting, temperature checks, and exudate amount and color.
6. **Do not** squeeze the wound or apply unprescribed creams or ointments.
7. **Antibiotics** only if clinically indicated by a provider.

---

**Summary:** The image shows a small, early-stage surgical or procedural wound in a skin-fold region, with scant yellow-reddish exudate, minimal visible erythema or edema, and no clearly visible closure material. Infection risk is low to moderate, raised mainly by the skin-fold location and the possible small wound opening. A clinical review within 24–48 hours is advised, with immediate care if signs of infection develop.

</details>


---

## 764.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | absent | absent | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | healed | healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Note:** This assessment is based on a single photograph and is not a substitute for in-person clinical evaluation.

---

### 1. Wound Location
- A linear incision on a hair-bearing skin surface with adjacent skin folds. This is most consistent with the **axillary or lateral chest wall region**, possibly the groin or inguinal area.
- The incision runs diagonally, roughly 6–8 cm of visible length, and follows the natural skin crease.

### 2. Wound Status
- **Healing phase:** Late proliferative or early remodeling phase. The incision appears **fully epithelialized**, with no gaping, dehiscence, or open areas along the line.
- **Scar appearance:** Slightly raised to flat, smooth and shiny, with a **pink-to-violaceous (purplish) discoloration**. This color is typical of an immature scar with active vascular remodeling.
- **Focal finding:** A **small dark punctate spot (~1–2 mm)** sits in the lower-middle part of the incision. Possible explanations:
  - a small dried scab or crust
  - a residual suture knot or a suture end working its way out ("spitting" suture)
  - less likely, a tiny sinus tract opening
- The skin around this punctum shows slightly deeper violaceous discoloration over a short segment.

### 3. Closure Method
- No external sutures, staples, or adhesive strips are visible.
- The fine, uniform linear scar suggests a **primary closure, likely with intradermal (subcuticular) absorbable sutures**, or with external sutures already removed.
- The punctate lesion may be a buried suture knot surfacing.

### 4. Exudate Characteristics
- **No visible exudate.** There is no serous, serosanguineous, or purulent drainage, and no wet or crusted discharge along the incision.
- No discharge is evident at the punctum, although it cannot be ruled out without palpation or pressure.

### 5. Erythema
- **No significant inflammatory erythema** extends beyond the scar margins.
- The pink-purple color is confined to the scar line itself, consistent with normal scar maturation rather than cellulitis.
- There is mild localized violaceous hue around the punctum, without spreading redness.

### 6. Edema
- **No obvious edema** or induration is visible. The surrounding skin keeps its normal texture and creases.
- The scar is slightly raised but not markedly swollen. Fluctuance cannot be judged from an image.

### 7. Urgency Level
- **Low (non-urgent / routine follow-up).**
- No signs of acute complication are present: no dehiscence, purulence, spreading redness, or significant swelling.
- At the next routine visit, a clinician should examine the punctum. If it is a spitting suture, it can be removed easily.

### 8. Infection Risk Assessment
- **Overall risk: Low.**
- **Favorable factors:** closed, epithelialized incision; no drainage; no peri-wound erythema or edema.
- **Mild concern:** the focal dark punctum with localized discoloration. A surfacing suture can sometimes cause a small stitch abscess or sinus. Body-fold locations like the axilla or groin also carry more moisture, friction, and bacteria, which raises baseline risk slightly.

---

### Recommendations
- Keep the area clean and dry, and avoid friction or tight clothing over the scar.
- Do not pick or squeeze the punctum.
- Seek prompt medical review if any of these develop:
  - increasing redness, warmth, pain, or swelling
  - discharge from the punctum or scar, especially pus or a foul odor
  - a palpable lump or fluctuance
  - fever or general malaise
- Arrange outpatient follow-up to inspect and, if needed, remove a residual suture.
- Once fully healed, consider scar care such as silicone gel or sheets and sun protection to reduce hypertrophic scarring.

</details>


---

## 803.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | absent | absent | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | not_healed | not_healed | healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based on a single photograph. It cannot replace an in-person exam by a qualified clinician. Lighting, angle, and resolution limit how accurately color, depth, and texture can be judged.

## 1. Wound Location
- **Site:** Forearm, most likely the volar (inner) or lateral surface, mid-to-distal segment.
- **Orientation:** A single linear incision running across the width of the forearm as photographed, perpendicular to the long axis of the limb.
- **Estimated length:** About 4–6 cm, judged against the forearm's width.

## 2. Wound Status
- **Healing phase:** Appears to be in the early-to-mid healing phase, likely the late inflammatory or early proliferative stage (roughly 7–14 days post-procedure, an estimate only).
- **Edge approximation:** The wound edges appear well approximated along the entire length, with no visible gaping or dehiscence.
- **Surface:** A thin, dark brown linear crust or scab lies along the incision line, consistent with normal epithelialization.
- **Integrity:** No visible open areas, separation, or tissue necrosis.

## 3. Closure Method
- **Likely method:** Interrupted sutures.
- **Evidence:** There are about 6–7 evenly spaced transverse marks crossing the incision, typical of interrupted suture placement.
- **Current state:** The cross-marks look dark and thin. Either the sutures are still in place (possibly dark nylon or silk) or they were recently removed, leaving suture tracks. In-person confirmation is needed.

## 4. Exudate Characteristics
- **Amount:** None visible.
- **Type:** No serous, serosanguineous, or purulent drainage is evident.
- **Wound bed:** Appears dry, with crusting consistent with normal healing.

## 5. Erythema
- **Assessment:** No significant erythema is visible.
- The surrounding skin appears to match the patient's baseline skin tone. There is no obvious spreading redness, streaking, or peri-incisional flare.
- Mild pinkness along the incision margins may be present, which is within normal limits for a healing wound.

## 6. Edema
- **Assessment:** No apparent edema.
- The forearm contour appears smooth and symmetric around the incision, with no visible localized swelling, puffiness, or tension on the suture line.

## 7. Urgency Level
**Low / Routine.**
- The wound appears to be healing as expected.
- Routine follow-up is recommended, such as a scheduled suture removal or wound check, typically 7–14 days after surgery for the forearm.
- No emergency intervention appears necessary based on this image.

## 8. Infection Risk Assessment
**Overall risk: Low.**

| Indicator | Finding |
|---|---|
| Purulent discharge | Absent |
| Erythema / cellulitis | Not evident |
| Edema / induration | Not evident |
| Wound dehiscence | Absent |
| Necrosis / discoloration | Absent |
| Foul odor, warmth, pain | Cannot be assessed from image |

**Patient-specific factors that would raise risk** (not determinable from the image): diabetes, smoking, immunosuppression, poor nutrition, or a contaminated or traumatic original wound.

## Recommendations
1. **Keep the wound clean and dry.** Follow the surgeon's instructions on showering and dressing changes.
2. **Suture removal:** If sutures are still in place, arrange removal at the interval the treating clinician specified (commonly 10–14 days for the forearm).
3. **Avoid strain:** Limit heavy lifting or excessive wrist and forearm flexion that could stress the incision.
4. **Scar care:** After full closure and suture removal, silicone gel or sheets and sun protection may improve scar appearance.
5. **Seek prompt medical attention if any of the following develop:**
   - Increasing redness, warmth, or swelling around the wound
   - Pus or cloudy or foul-smelling drainage
   - Wound edges separating
   - Fever (>38 °C / 100.4 °F) or chills
   - Worsening pain, red streaks extending up the arm
   - Numbness, tingling, or weakness in the hand, which is relevant given the forearm location and nearby nerves and tendons

**Summary:** A linear, well-approximated forearm surgical incision closed with interrupted sutures. It shows no visible signs of infection, exudate, erythema, or edema and appears to be healing normally. Urgency is low, and routine follow-up is advised.

</details>


---

## 808.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | non_purulent | none | NO |
| healing | unclear | healed | healed | n/a |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based only on a single photograph and cannot replace an in-person evaluation by a qualified clinician. Image resolution, lighting, and angle limit how accurately the findings can be interpreted.

## 1. Wound Location
- The wound appears to be on the **trunk**, most likely the lateral abdomen, flank, or lower back, judging by the skin contour and the clothing being held back.
- It is a **short linear incision**, roughly a few centimeters long, running diagonally downward.
- The soft, smooth skin and the fleece clothing suggest the patient may be a child.

## 2. Wound Status
- The incision appears **largely closed and in the healing phase**. The edges are well approximated along most of the length.
- The scar line looks **pink to slightly violaceous**, which fits an early-to-intermediate healing stage (likely several weeks after surgery).
- At the **upper end**, there is a **small, raised, punctate red-purple spot** with a slightly shiny, whitish rim. This could be:
  - a small area of **hypergranulation** or a **suture granuloma**,
  - a **retained or "spitting" absorbable suture**, or
  - a tiny residual scab or superficial opening.
- A second, smaller **dark point at the lower end** of the incision may be a similar suture reaction or a healing puncture site.

## 3. Closure Method
- **No external sutures, staples, or adhesive strips are visible.**
- The neat, linear scar suggests **primary closure**, possibly with absorbable subcuticular sutures or skin adhesive. The changes at both ends would fit reactions to buried suture knots, which commonly sit at the ends of the incision.

## 4. Exudate Characteristics
- **No obvious active drainage** (purulent, serous, or bloody) is visible.
- The red spot at the upper end may contain a **small amount of dried blood or serosanguineous material**, but there is no sign of pus or ongoing discharge.

## 5. Erythema
- **Mild, localized pinkness** is seen along the scar line and immediately around the upper-end lesion.
- There is **no spreading redness** into the surrounding skin. The skin around the wound looks normal in color.
- This degree of redness is consistent with normal scar maturation or a minor local suture reaction rather than cellulitis.

## 6. Edema
- There is **slight raising of the scar line** and the upper-end lesion, but **no significant surrounding swelling** is evident.
- Firmness, warmth, or a collection under the skin cannot be judged from the image.

## 7. Urgency Level
**Low to moderate (non-urgent, but review advised).**
- The wound does not appear to need emergency care.
- A **routine follow-up with the surgeon or primary clinician within the next several days** is reasonable to examine the spots at the ends. A retained suture may need to be removed, or hypergranulation may need simple treatment (such as silver nitrate).

## 8. Infection Risk Assessment
**Overall risk: Low, with a localized area to monitor.**

| Factor | Observation | Concern Level |
|---|---|---|
| Purulent discharge | Not seen | Low |
| Spreading erythema | Absent | Low |
| Significant swelling | Not apparent | Low |
| Wound opening | Possible tiny opening/granuloma at upper end | Mild |
| Suture reaction | Likely at one or both ends | Mild (can lead to a local infection or a small sinus) |

**Seek prompt medical attention if any of the following develop:**
- Increasing redness, warmth, or spreading pinkness around the incision
- Pus, cloudy or foul-smelling drainage
- Increasing pain or tenderness
- Swelling or a fluctuant (soft, fluid-filled) lump under the scar
- Fever, irritability, or the patient seeming unwell (especially important in a child)
- The wound edges separating

## 9. Recommendations
- Keep the area **clean and dry**. Gently clean it with mild soap and water, and pat it dry.
- **Avoid picking at or squeezing** the red spot.
- Wear loose, soft clothing to reduce friction (the current fleece appears suitable).
- Arrange a **clinical review** to check for a retained suture or hypergranulation tissue.
- Once the wound is fully healed, scar care such as silicone gel and sun protection may help the scar mature.

**Summary:** A healing, primarily closed linear surgical incision on the trunk with mild expected scar pinkness. Small punctate lesions at the incision ends are most consistent with a suture reaction or hypergranulation. There are no clear signs of active infection. Non-urgent clinical follow-up is recommended.

</details>


---

## 843.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | present | present | absent | yes |
| infection | elevated | elevated | elevated | yes |
| exudate | purulent | purulent | none | yes |
| healing | not_healed | not_healed | not_healed | yes |

<details><summary>Full report</summary>

# Wound Assessment Report

**Important:** This report is based only on visual analysis of a single photograph. It does not replace in-person clinical evaluation by a qualified healthcare provider.

---

## 1. Wound Location
- **Region:** Ankle, likely the **lateral or medial malleolar / supramalleolar area**, just above and slightly behind the malleolus.
- **Laterality:** Cannot be determined with certainty from the image.
- **Surrounding anatomy:** Heel and plantar surface visible below. The skin of the heel and foot appears dry and scaly (xerosis).

## 2. Wound Status
- **Type:** Small, open, **non-healed wound with an ulcerated or dehisced appearance**. It is roughly oval, about 1–1.5 cm in size (estimated, no scale reference).
- **Wound bed:** Reddish-dark tissue with a central depression. There may be some granulation tissue mixed with crust or slough at the margins.
- **Satellite lesions:** **Two to three small yellowish, raised, crusted papules or pustule-like lesions** sit just superior to the main wound.
- **Healing phase:** Appears to be in a **delayed or impaired healing phase**. There is no clear epithelial advancement from the edges.

## 3. Closure Method
- **No sutures, staples, adhesive strips, or tissue adhesive are visible.**
- The wound appears to be healing by **secondary intention**, or a primary closure has **dehisced or broken down**.

## 4. Exudate Characteristics
- **Amount:** Scant to low. No active drainage or pooling is visible.
- **Type:** Dried **yellowish crusting** at the wound margins and on the satellite lesions suggests a **seropurulent or purulent** component.
- **Odor:** Cannot be assessed from the image.

## 5. Erythema
- **Present.** There is a **dusky red to violaceous discoloration and hyperpigmentation** around the wound, extending about 1–2 cm.
- On darker skin tones, erythema may look brown or purple. The perilesional discoloration here is consistent with **inflammation**.

## 6. Edema
- **Mild localized swelling is possible** around the wound, with slight fullness of the periwound tissue.
- No obvious generalized ankle or foot edema is seen. Pitting cannot be assessed.

## 7. Urgency Level
**Moderate (semi-urgent): clinical review within 24–48 hours is recommended.**

Reasons:
- Non-healing open wound over a bony prominence
- Possible purulent satellite lesions, suggesting local infection or spread
- Periwound inflammation

The wound should be **escalated to urgent care** if any of the following develop:
- Fever or chills
- Rapidly spreading redness or red streaking up the leg
- Increasing pain, warmth, or swelling
- Foul-smelling or increased purulent drainage
- Black or necrotic tissue

## 8. Infection Risk Assessment
**Risk level: Moderate to High**

| Factor | Finding | Significance |
|---|---|---|
| Purulent-appearing crusts | Present | Suggests local bacterial infection (e.g., *Staphylococcus aureus*, *Streptococcus*) |
| Satellite pustules | Present | Possible local spread or folliculitis; consider impetiginization |
| Periwound erythema/discoloration | Present | Local inflammatory response |
| Location over malleolus | Yes | Thin soft tissue, pressure and friction exposure, slower healing |
| Dry, scaly skin | Present | Compromised skin barrier |
| Delayed healing | Likely | Raises concern for underlying factors |

**Differential considerations:**
- Surgical site infection or wound dehiscence
- Infected traumatic wound or ulcer
- Pressure or friction ulcer over the malleolus
- Venous or arterial insufficiency ulcer (check vascular status)
- Diabetic foot or ankle ulcer (check glucose and neuropathy)
- Ecthyma or impetigo with secondary ulceration

## 9. Recommendations
1. **In-person assessment:** Measure wound size and depth, probe for undermining or bone, and check temperature and tenderness.
2. **Wound culture:** Swab after cleansing (Levine technique) if infection is suspected.
3. **Vascular and metabolic screening:** Check pedal pulses, ABI if indicated, blood glucose or HbA1c, and CBC/CRP if there are systemic signs.
4. **Wound care:**
   - Gentle cleansing with saline
   - Debridement of crust or slough as appropriate
   - Moist wound environment, with antimicrobial dressings such as silver or iodine if infection is suspected
5. **Antibiotics:** Topical or systemic therapy as clinically indicated, guided by culture.
6. **Skin care:** Moisturize the dry, scaly skin of the foot and heel, and offload pressure from the ankle.
7. **Follow-up:** Reassess in 48–72 hours, and document with serial photographs including a measurement scale.

---
*Summary: Small, open, non-healing ankle wound with crusted, possibly purulent satellite lesions and periwound inflammation. No closure device is visible. Moderate urgency, with a moderate-to-high infection risk. Prompt clinical evaluation is advised.*

</details>


---

## 893.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | absent | absent | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | healed | not_healed | healed | NO |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based on a single photograph of limited resolution, and the image appears to be a staged or stock clinical photo. It is not a substitute for in-person examination by a qualified clinician.

## 1. Wound Location
- **Site:** Anterior/anteromedial aspect of the knee, extending obliquely over the patellar region.
- **Laterality:** Cannot be determined with certainty from this image.
- **Context:** The incision's position and orientation are consistent with prior knee surgery, such as arthroplasty or an open orthopedic procedure.

## 2. Wound Status
- **Healing phase:** Appears to be in the late healing or remodeling (maturation) phase.
- **Appearance:** Linear incision line that looks closed, with a thin, slightly darker brownish-red line.
- **Wound edges:** Well approximated. No visible dehiscence, gaping, or separation.
- **Wound bed:** No open area, granulation tissue, slough, or eschar is visible.
- **Overall:** Consistent with a healed or nearly healed surgical scar.

## 3. Closure Method
- **Current state:** No sutures, staples, or adhesive strips are visible.
- **Likely interpretation:** Closure material has been removed, or absorbable subcuticular sutures were used. Faint marks along the line may be residual suture or staple marks, but this is not definitive.

## 4. Exudate Characteristics
- **Amount:** None visible.
- **Type:** Not applicable. No serous, sanguineous, serosanguineous, or purulent drainage is seen.
- **Dressing:** None present, which is consistent with a closed, dry wound.

## 5. Erythema
- **Assessment:** No significant erythema around the incision.
- **Notes:** The scar has mild pigmentation (pink-brown), which is typical of a maturing scar. There is no spreading redness or streaking.

## 6. Edema
- **Assessment:** No obvious localized swelling around the incision.
- **Limitations:** Mild periarticular swelling cannot be fully excluded from a photograph. Comparison with the other knee and palpation would be needed.
- **Other findings:** The skin of the lower leg shows age-related changes and scattered small pigmented spots (likely benign lesions or seborrheic changes). There is no obvious pitting edema.

## 7. Urgency Level
- **Classification:** 🟢 **Low / Routine.**
- **Recommendation:** Routine follow-up per the surgical team's post-operative schedule. No urgent intervention appears needed based on visual findings.

## 8. Infection Risk Assessment
- **Current risk:** **Low.**
- **Supporting findings:**
  - Closed, well-approximated incision
  - No exudate or purulence
  - No periwound erythema or visible swelling
  - No signs of dehiscence or necrosis
- **Patient factors to consider:** The patient appears to be older. Age, diabetes, obesity, smoking, immunosuppression, and joint implants can raise the risk of late or deep infection, so clinical history should be reviewed. If an implant is present, periprosthetic joint infection should remain a consideration if symptoms develop.

## Recommendations
1. Continue routine scar care: keep the area clean and dry, protect it from the sun, and consider silicone gel or massage once it is fully epithelialized.
2. Continue rehabilitation or physiotherapy for knee range of motion if this followed an orthopedic procedure.
3. **Watch for warning signs that need prompt medical review:**
   - New or increasing redness, warmth, or swelling
   - Any drainage from the incision
   - Wound opening
   - Fever or chills
   - Increasing knee pain, stiffness, or reduced function
   - Calf pain or swelling (to rule out deep vein thrombosis)
4. Attend the scheduled follow-up with the surgical or orthopedic team.

**Summary:** The visible knee incision appears well healed, with no clinical signs of infection, inflammation, or complications. The urgency level is low and routine follow-up is appropriate.

</details>


---

## 924.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | present | present | absent | yes |
| edema | absent | absent | absent | yes |
| infection | low | low | low | yes |
| exudate | none | none | none | yes |
| healing | not_healed | not_healed | not_healed | yes |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based solely on a single photograph and cannot replace in-person evaluation by a qualified clinician. Uneven lighting (warm on the left, cooler on the right) limits color accuracy.

---

### 1. Wound Location
- **Region:** Lower back, lumbosacral area
- **Description:** Two vertical incisions, one on each side of the midline (bilateral paraspinal/para-sacral region), roughly symmetric, each about 4–6 cm long.
- **Additional finding:** A faint, pale, linear vertical scar in the **midline**, consistent with an older, fully healed incision from a prior procedure.
- **Possible context:** This pattern is consistent with bilateral minimally invasive spinal or sacroiliac procedures, but the image cannot confirm the procedure type.

### 2. Wound Status
- **Healing phase:** Early-to-mid proliferative phase. The wounds look approximately 1–3 weeks post-op.
- **Edge approximation:** The edges appear well approximated along most of their length, with no visible gaping or dehiscence.
- **Surface:** Thin areas of dried scab/crust along the incision lines. The tissue looks pink-to-violaceous, consistent with new granulation and epithelialization.
- **Surrounding skin:** Mild brownish periwound discoloration. This may be resolving bruising, post-inflammatory hyperpigmentation, or residual antiseptic/adhesive staining.
- **Overall:** Healing by primary intention appears to be progressing normally.

### 3. Closure Method
- No external sutures, staples, or adhesive strips are visible.
- The likely closure is **absorbable subcuticular sutures** and/or **tissue adhesive** (skin glue), or sutures/staples that have already been removed.
- The midline scar shows a mature, healed linear closure.

### 4. Exudate Characteristics
- **Amount:** None visible
- **Type:** No serous, sanguineous, or purulent drainage evident
- **Odor:** Cannot be assessed from the image
- The wounds appear dry, with crusting only.

### 5. Erythema
- **Present:** Minimal. There is a mild pink/dusky hue confined to the immediate incision line, which is expected during healing.
- **Spreading erythema:** None apparent. No redness extends beyond about 1 cm from the wound edges.
- **Note:** The violaceous tone and surrounding brown discoloration are more consistent with bruising or pigment change than with inflammatory erythema. The lighting makes this harder to judge.

### 6. Edema
- **Present:** Not evident
- The incisions sit slightly recessed, with no visible swelling, induration, or raised periwound tissue. Palpation would be needed to confirm there is no underlying fluid collection (seroma).

### 7. Urgency Level
- **Low / routine.** No features suggest a need for urgent intervention.
- **Recommendation:** Continue routine wound care and keep the scheduled post-operative follow-up.

### 8. Infection Risk Assessment
- **Current risk:** **Low**
- **Favorable signs:** Intact, approximated edges; no purulent drainage; no spreading erythema; no visible swelling; dry wound beds.
- **Factors to monitor:**
  - The lumbosacral location is close to the waistband and subject to friction, moisture, and sweat.
  - Proximity to the gluteal cleft carries some contamination risk.
  - Patient-specific risks such as diabetes, smoking, obesity, or immunosuppression are unknown.

**Seek prompt medical review if any of the following develop:**
- Increasing redness, warmth, or redness spreading from the incisions
- New swelling, firmness, or fluctuance (a soft, fluid-filled feel)
- Cloudy, yellow/green, or foul-smelling drainage
- Wound edges separating
- Fever (>38°C / 100.4°F), chills, or worsening pain
- New neurological symptoms in the legs, if this was a spinal procedure

### Care Recommendations
- Keep the incisions clean and dry, and let scabs separate naturally without picking.
- Avoid tight waistbands rubbing over the incisions.
- Follow the surgeon's instructions on showering and avoid soaking (baths, pools) until cleared.
- Once fully epithelialized and cleared by the surgeon, consider sun protection and silicone scar products to reduce hyperpigmentation.

---
**Summary:** Bilateral lumbosacral surgical incisions in the early-to-mid healing phase, well approximated, dry, with no visible signs of infection. There is also a healed older midline scar. Urgency is low and infection risk is low. Continue routine monitoring and follow-up.

</details>


---

## 966.jpg

| attribute | hand label | checker | surgeon | agreement |
|---|---|---|---|---|
| erythema | absent | absent | present | yes |
| edema | present | present | None | yes |
| infection | elevated | elevated | low | yes |
| exudate | non_purulent | none | none | NO |
| healing | not_healed | (none) | not_healed | NO |

<details><summary>Full report</summary>

# Surgical Wound Assessment Report

**Disclaimer:** This assessment is based solely on a single photograph and is intended for informational and educational purposes. It does not replace in-person evaluation by the treating surgical or wound-care team.

---

### 1. Wound Location
- **Site:** Dorsum of the foot (forefoot to midfoot), extending distally toward the bases of the lesser toes (2nd–4th web spaces region).
- **Approximate extent:** A large, irregular, roughly quadrilateral defect covering much of the dorsal forefoot. It spans from the metatarsal heads proximally toward the mid-dorsum, about 6–8 cm × 5–7 cm by visual estimate.
- **Adjacent structures:** The toes show focal discoloration (greenish-yellow and purplish bruising) near the nail folds and the 3rd–4th toe region. The surrounding skin of the ankle and leg appears intact and dry.

### 2. Wound Status
- **Type of repair:** The appearance is consistent with a **meshed split-thickness skin graft (STSG)**. A fine cross-hatched (mesh) pattern is visible across the wound bed.
- **Graft appearance:**
  - Predominantly **pink-red to violaceous/purple**, with darker purplish patches scattered across the surface, especially centrally and laterally.
  - Some areas look yellowish-tan, which may be fibrinous material or early epithelialization within the mesh interstices.
- **Healing phase:** This is likely the early postoperative period (roughly 5–10 days post-grafting), given the retained sutures and the immature graft color.
- **Graft take:** It appears to be **partial to moderate take**. Pink areas suggest revascularization. The darker purple and dusky zones raise concern for hematoma or seroma under the graft, venous congestion, or areas of poor adherence or early graft loss. These areas need close inspection.

### 3. Closure Method
- **Primary method:** Meshed split-thickness skin graft.
- **Fixation:** Multiple **interrupted sutures or staples** are visible around the graft perimeter, with long suture tails left in place. These are commonly used to secure a tie-over bolster dressing, which appears to have been removed.
- **Margins:** Graft edges appear generally apposed to the surrounding skin. Mild irregularity is present at the proximal-lateral border.

### 4. Exudate Characteristics
- **Amount:** Minimal to none visible. There is no pooling or soaking.
- **Type:** Small areas of dried serosanguinous material and possible fibrin near the margins.
- **Odor/purulence:** No frank purulent exudate is visible. Odor cannot be assessed from an image.

### 5. Presence of Erythema
- **Peri-wound skin:** No significant spreading erythema is seen in the surrounding skin of the foot or ankle.
- **Graft itself:** The red-purple coloration is largely intrinsic to an immature graft. It should not be confused with cellulitis, but the darker violaceous zones warrant monitoring.
- **Toes:** Focal discoloration (green-yellow and purple) of the toes suggests resolving bruising. Tissue perfusion should also be checked.

### 6. Presence of Edema
- **Mild edema** of the dorsal foot and toes appears likely. The toes look somewhat swollen, and the skin around the ankle shows fine wrinkling and a slightly shiny texture.
- No marked pitting or tense swelling can be confirmed from the image.

### 7. Urgency Level
**Moderate – timely follow-up required (within 24–48 hours). This is not an emergency based on the image alone.**

Rationale:
- The graft is partially viable, with no obvious signs of acute infection.
- However, the dusky and purple areas raise concern for compromised graft take, hematoma or seroma, or ischemia.
- The toe discoloration should be checked to confirm adequate distal circulation.

**Escalate to urgent review** if any of the following occur:
- Increasing pain
- Purulent drainage or foul odor
- Spreading redness
- Fever
- Blackening of the graft or toes
- Cool or pale toes
- Rapidly worsening swelling

### 8. Infection Risk Assessment
**Overall risk: Moderate**

| Factor | Assessment |
|---|---|
| Location (foot, distal extremity) | ↑ Risk: high bacterial load and dependent edema |
| Large graft surface area | ↑ Risk |
| Possible areas of non-adherent or congested graft | ↑ Risk: hematoma or seroma can become infected and threaten graft survival |
| Visible purulence | Not observed (favorable) |
| Peri-wound cellulitis | Not observed (favorable) |
| Exudate | Minimal (favorable) |
| Comorbidities (e.g., diabetes, PVD, smoking) | Unknown. If present, these would significantly raise the risk |

### 9. Recommendations
1. **Clinical inspection of the graft:**
   - Assess adherence and capillary refill of the dusky areas.
   - Evacuate any underlying hematoma or seroma if present.
2. **Vascular check:** Assess toe perfusion (capillary refill, temperature, pulses), particularly given the toe discoloration.
3. **Wound care:**
   - Use a non-adherent dressing (e.g., petrolatum gauze or silicone mesh) with a moist environment.
   - Consider removing the remaining sutures or staples at the appropriate interval.
4. **Edema control:**
   - Elevate the limb.
   - Limit dependency and weight-bearing as directed by the surgeon.
   - Use gentle compression only once the graft is stable.
5. **Infection surveillance:**
   - Monitor for fever, pain, odor, purulence, and spreading erythema.
   - Take a swab or culture if signs develop.
6. **Systemic optimization:**
   - Glycemic control if diabetic.
   - Nutritional support.
   - Smoking cessation.
7. **Follow-up:** Reassess within 48–72 hours to document graft take percentage and progression.

---

**Summary:** This is a meshed split-thickness skin graft on the dorsal forefoot in the early postoperative phase. It shows partial take with areas of dusky or violaceous discoloration, minimal exudate, no evident cellulitis, and mild edema. Infection risk is moderate. Prompt clinical review is advised to evaluate graft viability and distal perfusion.

</details>

