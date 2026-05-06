import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
from scipy.ndimage import gaussian_filter
from Objects import SPECIES_LIST

# Configuration
SIZE = 50
DAYS = 365*10
WATER, EMPTY = -1, 0  # Water is -1, empty land is 0, tree heights start from 1 upwards
DROUGHT_DEATH_CHANCE = 0.2
TREE_HEIGHT_SCALE = 0.02
current_year = 0
# --- 1. WORLD GENERATION ---
def generate_world(size):
    # 1. Base Elevation
    noise = np.random.rand(size, size)
    elevation = gaussian_filter(noise, sigma=5)
    elevation = (elevation - elevation.min()) / (elevation.max() - elevation.min())
    
    # 2. Natural Steepness (from slope)
    dy, dx = np.gradient(elevation)
    base_steepness = np.sqrt(dx**2 + dy**2)
    base_steepness = (base_steepness - base_steepness.min()) / (base_steepness.max() - base_steepness.min())
    
    # 3. Add Semi-Random Ruggedness
    # We create a separate high-frequency noise map for "rocks"
    rugged_noise = np.random.rand(size, size)
    rugged_noise = gaussian_filter(rugged_noise, sigma=1) # Sigma 1 = very sharp/jagged
    
    # 4. Blend them (70% natural slope, 30% random ruggedness)
    steepness = (base_steepness * 0.4) + (rugged_noise * 0.6)
    flow_map = np.zeros((size, size, 2), dtype=int)
    for i in range(size):
        for j in range(size):
            y_min, y_max = max(0, i-1), min(size, i+2)
            x_min, x_max = max(0, j-1), min(size, j+2)
            neighborhood = elevation[y_min:y_max, x_min:x_max]
            local_y, local_x = np.unravel_index(np.argmin(neighborhood), neighborhood.shape)
            flow_map[i, j] = [y_min + local_y, x_min + local_x]
            
    water_mask = elevation < np.percentile(elevation, 2) # We set water at the lowest 2% of elevations to create more lakes and rivers, which are crucial for a thriving forest ecosystem.
    return elevation, steepness, water_mask, flow_map

ELEV, STEEP, WATER_MAP, FLOW = generate_world(SIZE)
grid = np.zeros((SIZE, SIZE))
species_grid = np.zeros((SIZE, SIZE), dtype=int)
# Initial Seeding (populating the world with trees based on elevation suitability and water presence)
for i in range(SIZE):
    for j in range(SIZE):
        # 1. Identify Water Basins (Static check for day 0)
        if ELEV[i, j] < np.percentile(ELEV, 7):
            grid[i, j] = WATER
        else:
            # 2. Elevation Suitability: Find species that can actually grow here
            valid_species = [
                idx for idx, s in enumerate(SPECIES_LIST) 
                if s.preferred_elev[0] <= ELEV[i, j] <= s.preferred_elev[1]
            ]
            
            if valid_species:
                s_idx = np.random.choice(valid_species)
                species_grid[i, j] = s_idx
                spec = SPECIES_LIST[s_idx]
                
                # 3. High Starting Density (80% coverage)
                if np.random.random() < 0.2:
                    # Plant trees based on their actual max height
                    grid[i, j] = np.random.choice([spec.max_height - 1, spec.max_height], p=[0.5, 0.5])
            else:
                # Fallback if no species fits the elevation
                species_grid[i, j] = np.random.randint(0, len(SPECIES_LIST))

yearly_cycle = (np.arange(DAYS) % 365) / 365
# 3. Plug that cycle into your original formulas
rain_history = 0.25 * (np.sin(2 * np.pi * yearly_cycle + np.pi/2)) + 0.25
annual_soil_moisture = 0.3 + (0.27 * (np.sin(2 * np.pi * yearly_cycle + np.pi/2)) + 0.3)

def get_tree_points(tree_grid):
    ys, xs = np.where(tree_grid > EMPTY)
    if len(xs) == 0:
        return [], [], [], [], []

    zs = []
    point_colors = []
    point_sizes = []
    for y, x in zip(ys, xs):
        state = tree_grid[y, x]
        spec = SPECIES_LIST[species_grid[y, x]]
        spec.current_height = state
        zs.append(ELEV[y, x] + (spec.current_height * TREE_HEIGHT_SCALE))
        point_colors.append(spec.color)

        if spec.current_height >= spec.max_height:
            point_sizes.append(18)
        elif spec.current_height == 1:
            point_sizes.append(8)
        else:
            point_sizes.append(12)

    return xs, ys, zs, point_colors, point_sizes

# --- 2. VISUALIZATION SETUP (4 PANELS) ---
fig = plt.figure(figsize=(15, 10))
gs = fig.add_gridspec(2, 4)

# Main Simulation
ax_sim = fig.add_subplot(gs[:, :2])
colors = ['#1f77b4', '#d2b48c', '#90ee90', '#32cd32', '#006400']
img = ax_sim.imshow(grid, cmap=ListedColormap(colors), vmin=-1, vmax=3)
ax_sim.set_title("Live Forest Succession")

# Elevation
ax_elev = fig.add_subplot(gs[0, 2])
ax_elev.imshow(ELEV, cmap='terrain')
ax_elev.set_title("Topography")
ax_elev.axis('off')

# Rain Rate
ax_rain = fig.add_subplot(gs[1, 2])
ax_rain.plot(rain_history, color='blue', alpha=0.3)
rain_marker, = ax_rain.plot([], [], 'ro')
ax_rain.set_title("Seasonal Rain")
ax_rain.set_ylim(0, 1.1)

ax_bars = fig.add_subplot(gs[:, 3])
names = [s.name for s in SPECIES_LIST]
bar_colors = [s.color for s in SPECIES_LIST]
bars = ax_bars.bar(names, [0]*len(names), color=bar_colors)
ax_bars.set_title("Greek Tree Population")
ax_bars.set_ylim(0, (SIZE*SIZE)//5) 
plt.setp(ax_bars.get_xticklabels(), rotation=45, ha="right") # Rotate names for clarity
stats_text = ax_sim.text(0.02, 0.95, '', transform=ax_sim.transAxes, color='white', 
                         fontweight='bold', bbox=dict(facecolor='black', alpha=0.6))

# Separate 3D terrain video
fig_3d = plt.figure(figsize=(10, 8))
ax_3d = fig_3d.add_subplot(111, projection='3d')
x_grid, y_grid = np.meshgrid(np.arange(SIZE), np.arange(SIZE))
ax_3d.plot_surface(x_grid, y_grid, ELEV, cmap='terrain', alpha=0.55,
                   linewidth=0, antialiased=False)
tree_x, tree_y, tree_z, tree_colors, tree_sizes = get_tree_points(grid)
tree_scatter = ax_3d.scatter(tree_x, tree_y, tree_z, c=tree_colors, s=tree_sizes,
                             depthshade=True)
ax_3d.set_title("3D Terrain: Tree Species")
ax_3d.set_xlim(0, SIZE - 1)
ax_3d.set_ylim(0, SIZE - 1)
ax_3d.set_zlim(0, 1 + (max(s.max_height for s in SPECIES_LIST) * TREE_HEIGHT_SCALE))
ax_3d.set_xlabel("X")
ax_3d.set_ylabel("Y")
ax_3d.set_zlabel("Elevation")
ax_3d.view_init(elev=35, azim=-60)
ax_3d.legend(handles=[
    mpatches.Patch(color=spec.color, label=spec.name)
    for spec in SPECIES_LIST
], loc="upper right")
# --- 3. ANIMATION ENGINE ---
def update(frame, img, grid, stats_text):
    global tree_scatter
    current_year = frame // 365
    new_grid = grid.copy()
    current_rain = rain_history[frame]
    rain_marker.set_data([frame], [current_rain])
    current_soil_moisture = annual_soil_moisture[frame]


    # Runoff
    moisture = np.full((SIZE, SIZE), current_rain + current_soil_moisture, dtype=float)
    for i in range(SIZE):
        for j in range(SIZE):
            if STEEP[i, j] > 0.15: #f a cell is relatively flat, the water stays put. If it’s steeper than the threshold, gravity takes over.
                ty, tx = FLOW[i, j];  # Find the target cell where water flows
                m_t = current_rain * 0.5 * STEEP[i, j] # The amount of water that moves is proportional to the rain and the steepness
                moisture[i, j] -= m_t; # Remove water from the current cell
                moisture[ty, tx] += m_t # Add it to the target cell

    # Evolution
    mature_counts = [0] * len(SPECIES_LIST)
    for i in range(SIZE):
        for j in range(SIZE):
            if grid[i, j] == WATER: continue
            state = grid[i, j]; s_idx = species_grid[i, j]; spec = SPECIES_LIST[s_idx]
            spec.current_height = state
            m, alt = moisture[i, j], ELEV[i, j]
            
            if spec.current_height == EMPTY:        
                r = spec.seed_range
                ys, ye = max(0, i-r), min(SIZE, i+r+1); xs, xe = max(0, j-r), min(SIZE, j+r+1)
                if np.any((grid[ys:ye, xs:xe] == spec.max_height) & (species_grid[ys:ye, xs:xe] == s_idx)):
                    if np.random.random() < (spec.growth_rate * m): new_grid[i, j] = 1 #
            elif spec.current_height > EMPTY:
                if spec.max_height-1 < spec.current_height <= spec.max_height:
                    # Mature trees can only die from thirst.
                    death_p = DROUGHT_DEATH_CHANCE if m < spec.water_need_for_grown_trees else 0.0
                else:
                    death_p = 0.005 + (alt * 0.01)
                    if m < spec.water_need: death_p += DROUGHT_DEATH_CHANCE

                if np.random.random() < death_p: new_grid[i, j] = EMPTY
                elif spec.current_height < spec.max_height:
                    if np.random.random() < spec.current_height * spec.growth_rate: new_grid[i, j] += spec.growth_rate
            
            # Count mature trees for the bar chart
            if new_grid[i, j] == spec.max_height:
                mature_counts[s_idx] += 1

    # Update Bar Chart
    for bar, count in zip(bars, mature_counts):
        bar.set_height(count)
        
    stats_text.set_text(f"Year: {current_year}| Day: {frame+1}/{DAYS} | Rain: {current_rain:.2f} | Rain (Year): {rain_history[frame]:.2f}")
    img.set_data(new_grid)
    tree_scatter.remove()
    tree_x, tree_y, tree_z, tree_colors, tree_sizes = get_tree_points(new_grid)
    tree_scatter = ax_3d.scatter(tree_x, tree_y, tree_z, c=tree_colors, s=tree_sizes,
                                 depthshade=True)
    ax_3d.view_init(elev=35, azim=-60+(frame*0.5)) # Slowly rotate the 3D view for better visualization
    fig_3d.canvas.draw_idle()

    grid[:] = new_grid[:]
    return img, stats_text, rain_marker, tree_scatter, *bars

plt.tight_layout()
ani = animation.FuncAnimation(fig, update, fargs=(img, grid, stats_text), 
                              frames=DAYS, interval=1, blit=False)
plt.show()
