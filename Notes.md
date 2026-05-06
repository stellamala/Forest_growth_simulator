# Forest Growth Simulator
@by Styliani Rafaela Maladaki

This project was created in order to try and **simulate** a **Mediterranean** forest growth. Using its elevation and **hydrological** parameters, like precipitation per day and soil moisture **retention** per day.

## Tree Types 

In this project right now there are five Greek tree types: 

**OLIVE**, **ALEPPO_PINE**, **HOLM_OAK**, **GREEK_FIR**, and **BLACK_PINE**

with each one of them being described by: 

1. **name**
2. **max height** [m]
3. **growth rate** [m/day]
4. **water need** (for growing trees) [mm per day]
5. **preferred elevation** [fraction of max elevation] 
> **NOTE:** this is used only for first map generation purposes.
6. **seed range** [pixel]
7. **color** (for plotting purposes)
8. **current height** [m]
9. **water need for grown trees** [mm per day] 

> **NOTE:** it is assumed to be half of the water need of growing trees, because as trees grow they become more drought resistant.

These characteristics are used to describe and differentiate between the different tree types.

# Map generation 
The map is generated based on several semi-random parameters. The purpose of this map was to describe adequately a Mediterranean elevation profile with **rugged** highs and lows.

## Elevation
For the elevation, first, two grids were created: one where a **Gaussian** filter was used to create a "smooth map" and the other a **rugged_noise** grid which was used to remove some of the smoothness of the first grid.

Combining the two into one map that is 70% natural slope and 30% random ruggedness.

## Water Bodies
Based on the elevation grid, the water bodies are designed to cover the lowest 2 percent of the elevation. 

## Hydrological Modeling
For this simulation, the hydrological dynamics that are described are **runoff**, **precipitation**, and **soil moisture**.

Every pixel has a soil moisture which is described based on a temporal graph (sin wave upside-down bell) in order to simulate the changing nature throughout the year based on the season. 

Precipitation follows the same logic as it is also simulated by a sin wave with a peak of 0.5 [mm/day] and a low of 0 [mm/day]. 

Runoff is estimated based on the water accumulation of a given pixel [mm/day], which is calculated based on the supply of water for each pixel:

> **Supply = soil moisture + precipitation + runoff from neighboring pixels**
 
With the slope of the neighboring cells defining if the water will "move on" to the lowest altitude neighboring cell.

# Tree growth simulation 
The simulation follows a daily cycle where every tree's life is decided based on its <b>current stage</b> and the <b>water supply</b>.

## Growth and Maturity
A tree starts as a **seedling** (Height = 1) and tries to reach its **max height**. 
* Every day, a tree has a chance to grow by 1 meter based on its **growth rate**.
* Once a tree reaches its max height, it is considered **Mature**.

## Survival and Death
The primary cause of death in this simulation is **thirst**.
* **Growing trees** (Height < max) are fragile. They need the full **water need** amount to survive. If the supply is lower, they have a high chance of dying.
* **Grown trees** (Height = max) are more resistant. They only need the **water need for grown trees** (half the original amount) to survive.
* If a tree dies, the pixel returns to **EMPTY** soil, allowing new seeds to take its place.

## Seed Dispersal (Reproduction)
Only **Mature** trees can reproduce. 
* Every day, mature trees check the empty pixels within their **seed range**.
* If an empty pixel is has enough moisture, there is a chance a new seedling of that species will sprout.