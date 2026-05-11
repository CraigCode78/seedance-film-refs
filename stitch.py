#!/usr/bin/env python3
"""Add crossfade transitions between shots and stitch into final film."""
import os, subprocess

shots_dir = '/tmp/seedance-film'
output = f'{shots_dir}/the_map_beneath_final.mp4'

# Build ffmpeg filter graph with crossfade transitions
shots = [f'{shots_dir}/shot{i:02d}.mp4' for i in range(1, 13)]

# Build a proper crossfade filter
# Each pair of consecutive clips gets a 0.5s crossfade
transition = 0.5

filter_parts = []
# First input doesn't need a fade-in
# Last output doesn't need a fade-out

chain = '[0:v]'
setpts_parts = []

# Build the chain: each clip gets a setpts, then crossfade with next
# Simpler approach: just concat with dissolve transitions

# Build concat with transitions
lines = []
# Simple concat first (just to make progress)
for i, shot in enumerate(shots):
    lines.append(f'file \'{shot}\'')

with open(f'{shots_dir}/concat_final.txt', 'w') as f:
    f.write('\n'.join(lines))

# For now, simple concat without crossfade - we can add effects later
cmd = [
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0',
    '-i', f'{shots_dir}/concat_final.txt',
    '-c', 'copy',
    '-movflags', '+faststart',
    output
]

print('Concatenating shots...')
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    size = os.path.getsize(output)
    print(f'Film complete: {output}')
    print(f'Size: {size:,} bytes ({size/1e6:.1f} MB)')
else:
    print(f'FFmpeg error: {result.stderr[-500:]}')

# Now try with crossfade transitions for better quality
print('\nNow building with crossfade transitions...')

# Build individual video inputs and crossfade chain
inputs = []
for i, shot in enumerate(shots):
    inputs.extend(['-i', shot])

# For 12 clips, chain 11 crossfades
# xfade filter: [0:v][1:v]xfade=transition=fade:duration=0.5:offset=T[v01]
# [v01][2:v]xfade=transition=fade:duration=0.5:offset=T2[v02]
# etc.

filter_graph = ''
offset = 0.0
duration = 5.0  # each shot is 5s
prev_label = '[0:v]'

for i in range(1, 12):
    next_label = f'[{i}:v]'
    if i < 11:
        out_label = f'[v{i:02d}]'
    else:
        out_label = f'[vout]'
    
    offset = i * duration - transition
    filter_graph += f'{prev_label}{next_label}xfade=transition=fade:duration={transition}:offset={offset}{out_label};'
    prev_label = out_label

filter_graph = filter_graph.rstrip(';')

cmd2 = [
    'ffmpeg', '-y',
] + inputs + [
    '-filter_complex', filter_graph,
    '-map', '[vout]',
    '-c:v', 'libx264',
    '-preset', 'medium',
    '-crf', '18',
    '-movflags', '+faststart',
    f'{shots_dir}/the_map_beneath_with_transitions.mp4'
]

print('Running crossfade version...')
result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=300)
if result2.returncode == 0:
    size = os.path.getsize(f'{shots_dir}/the_map_beneath_with_transitions.mp4')
    print(f'Film with transitions complete: {size:,} bytes ({size/1e6:.1f} MB)')
else:
    print(f'FFmpeg transition error: {result2.stderr[-500:]}')
