 Blender Terrain Generator
 
A Blender addon that generates 3D terrain using fractal noise (Fractal Brownian Motion)
combined across multiple octaves. The result is a naturally-looking, procedurally structured
terrain with configurable hills and detail levels.
 
![Terrain preview](preview.png)
 
## How it works
 
Terrain height is computed by layering multiple noise octaves with different frequencies
and amplitudes. Hills are placed randomly and blended smoothly into the base terrain
using a smoothstep function to avoid sharp edges.
 
## Installation
 
1. Download `terrain_generator.py`
2. In Blender: **Edit → Preferences → Add-ons → Install**
3. Select the file and enable the addon
4. In the 3D Viewport press **N** → open the **Make Terrain** tab
## Parameters
 
| Parameter       | Description                           |
|-----------------|---------------------------------------|
| Subdivisions    | Grid resolution                       |
| Seed            | Change for different terrain layout   |
| Noise Strength  | Overall terrain roughness             |
| Noise Detail    | Number of noise octaves               |
| Number of Hills | How many hills to place               |
| Hill Smoothness | How smoothly hills blend into terrain |
