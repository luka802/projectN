# Midnight Premiere artwork

Created with the built-in ImageGen tool from the user's selected Midnight Premiere concept. These are original illustrative assets, not official studio posters or actor photographs. Titles and metadata are rendered separately as HTML; search never depends on text embedded in an image.

## Saved project assets

- `static/art/coastal-hero.png`: original Coastal Escape travel hero photograph.
- `static/art/coastal-destinations.png`: three equal destination panels (Beach, Mountains, City break), displayed through CSS background positioning.

### Coastal Escape prompts

Hero: "Use case: photorealistic-natural. Asset type: travel website hero background. Create a wide landscape photograph, 1536x1024, Mediterranean turquoise cove with clear water, pale limestone coastal cliffs and green pine trees, small distant white sailboats, bright clear blue sky, refined editorial travel photography, natural sunlit color. Composition: coastline and strongest detail concentrated right half, open sea and sky across left for later CSS overlay. No text, UI, logos or watermarks. Realistic, inviting, serene."

Destination atlas: "Use case: photorealistic-natural. Asset type: destination photographs atlas for travel planner website. One landscape image divided into exactly THREE EQUAL VERTICAL PANELS edge-to-edge, no borders or gutters. Left third: sparkling turquoise Mediterranean cove, pale sand and pines, sunny blue sky. Middle third: beautiful alpine mountains and evergreen trees reflected in a blue lake, sunny clear day. Right third: warm historic European city by a river, stone bridge and domed architecture, inviting late afternoon golden light. Each panel is an independent portrait photograph with matching professional editorial photography quality. Absolutely no lettering, captions, UI, logos, watermark, or collage overlaps. Output 1536x1024 landscape, equal thirds."

### Cinema assets

- `static/art/hero.png`: landscape hero background.
- `static/art/interstellar.png`: individual space-film artwork.
- `static/art/inception.png`: individual dream-city artwork.
- `static/art/memento.png`: individual noir-memory artwork.
- `static/art/genres.png`: six-panel genre artwork atlas used through CSS background positioning, without distorting the source images.

All artwork is served locally. No movie-poster API key, remote poster service, or additional runtime image generation is needed.

## Final prompt set

The selected concept image was an art-direction reference for each generation, not a screenshot to embed as the website.

### Hero

Use case: photorealistic-natural. Create a brand new 1536x1024 landscape cinematic website background. Input image is ONLY an art-direction reference; DO NOT reproduce UI, text, posters, logos, or the screenshot. Scene: a lone astronaut seen from behind on an alien rocky plain, standing in the RIGHT third of frame, gazing toward a huge luminous black hole and sweeping starfield on the RIGHT. Left half mostly dark charcoal-black empty terrain/sky with restrained distant stars, suitable for readable white/red HTML headline overlaid later. Premium dramatic realism, silver starlight, subtle warm ring glow, rich blacks. Match the Midnight Premiere reference atmosphere. No text, no typography, no borders, no watermark.

### Interstellar artwork

Use case: ads-marketing. Original cinematic portrait artwork for a movie website, 1024x1536, no text or lettering whatsoever. Input screenshot ONLY art-direction reference. A solitary astronaut seen from behind on a cold pale extraterrestrial landscape, enormous sweeping Milky Way and glowing stellar dust filling upper two thirds. Photoreal movie-poster composition, deep navy-black, icy silver and restrained warm starlight. Strong visual focal point, expensive dramatic film photography. Leave lower edge dark for later HTML title. No UI, no titles, no credits, no logos, no watermarks.

### Inception artwork

Use case: ads-marketing. Original cinematic portrait artwork 1024x1536 for a film-discovery website, no text. Screenshot ONLY art-direction reference. A lone sharply dressed man seen from behind, standing at edge of a monumental city whose streets and skyscrapers fold upward into impossible architecture. Cool blue-grey light, deep shadow, subtle red accent, intricate realistic city detail, psychological dream-thriller atmosphere. Beautiful cohesive professional film-poster composition; lower edge dark for HTML typography later. No UI, no titles, no credits, no logos, no watermarks.

### Memento artwork

Use case: ads-marketing. Original cinematic portrait artwork 1024x1536 for a film-discovery website, no text. Screenshot ONLY art-direction reference. Psychological noir mystery collage: close-up of an anonymous blond man's intense eyes and face in shadow, overlapping blank Polaroid photographs, fragments of handwritten-looking abstract marks that are NOT legible words, sepia paper, small silhouettes and fractured reflections. Moody amber, ivory and charcoal palette, expressive photographic texture, professional movie-poster composition; lower edge dark for later HTML title. No UI, no film title, no real actor likeness, no logos, no watermark.

### Genre atlas

Use case: ads-marketing. One square 1536x1536 cinematic artwork sprite sheet, EXACTLY three equal columns and two equal rows, six edge-to-edge panels with absolutely no gutters, borders, labels, lettering or text. Each individual panel is portrait 2:3, 512x768. Original photoreal cinematic movie-poster artwork, refined charcoal palette and dramatic lighting matching the reference. TOP LEFT: horror, isolated misty farmhouse at night with a warm ominous window and dark trees. TOP MIDDLE: heartfelt drama, two anonymous friends standing together under warm golden light on a rooftop. TOP RIGHT: fantasy animation atmosphere, magical lush forest with glowing distant spirits, painterly cinematic, no copied characters. BOTTOM LEFT: romance, two anonymous people apart beneath warm lights of a European city street at dusk. BOTTOM MIDDLE: action thriller, lone figure against monumental dark city architecture and headlights. BOTTOM RIGHT: science fiction, a mysterious spacecraft above a misty alien landscape. No faces resembling known actors, no titles, no UI, no watermark. Precise six equal rectangular compositions as a sprite atlas.

## Typography

Anton supplies the condensed cinematic headline and brand. DM Sans and Manrope cover supporting UI text. Original font files and OFL licenses are bundled under `static/fonts/`.

## Movie Lounge update

`static/art/lounge-hero.png` is the original locally served home-cinema background. Existing film artworks are retained, shown in compact landscape frames with titles as separate HTML text. They are illustrative images, not official posters.

Generation prompt: "Use case: photorealistic-natural. Asset type: wide movie-discovery website hero background, 1536x1024 landscape. Premium cozy home cinema at night, dark charcoal room, warm amber practical lamplight on right, softly glowing large television in upper right showing an indistinct cinematic sunset city scene with tiny anonymous silhouettes, textured sofa with soft throw lower right, bowl of popcorn nearby. Left 55 percent is quiet near-black charcoal negative space for readable website headline overlay, no people in the room, no text, no lettering, no logos, no UI, no watermarks. Photoreal cinematic still with crisp natural textures and controlled subtle warm lighting, muted amber and deep blue-black, no red, no oversaturated neon. Details and highlights right of center. Elegant movie-night atmosphere."
