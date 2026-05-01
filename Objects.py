class TreeSpecies:
    def __init__(self, name, max_height, growth_rate, water_need, preferred_elev, seed_range, color):
        self.name = name
        self.max_height = max_height
        self.growth_rate = growth_rate
        self.water_need = water_need
        self.preferred_elev = preferred_elev
        self.seed_range = seed_range
        self.color = color

# --- Greek Tree Species ---

# 1. Olive (Olea europaea): Lowland, very drought resistant, slow growth
OLIVE = TreeSpecies("Olive", 2, 0.15, 0.10, (0.0, 0.3), 2, '#808000')

# 2. Aleppo Pine (Pinus halepensis): Classic coastal pine, medium elevation
ALEPPO_PINE = TreeSpecies("Aleppo Pine", 3, 0.30, 0.20, (0.1, 0.5), 4, '#2E8B57')

# 3. Holm Oak (Quercus ilex): Hardy evergreen oak found across middle elevations
HOLM_OAK = TreeSpecies("Holm Oak", 3, 0.20, 0.35, (0.3, 0.7), 2, '#006400')

# 4. Greek Fir (Abies cephalonica): High altitude, needs more moisture
GREEK_FIR = TreeSpecies("Greek Fir", 3, 0.18, 0.50, (0.6, 0.9), 3, '#004225')

# 5. Black Pine (Pinus nigra): Found on the highest mountain peaks
BLACK_PINE = TreeSpecies("Black Pine", 3, 0.12, 0.30, (0.7, 1.0), 3, '#1A2421')

SPECIES_LIST = [OLIVE, ALEPPO_PINE, HOLM_OAK, GREEK_FIR, BLACK_PINE]