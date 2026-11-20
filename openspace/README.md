# OpenSpace export

`csm_openspace.py` turns the Betelgeuse CSM surface-density map (`saved_data/csm_2d_density.csv`) into two point clouds
and an asset for [OpenSpace](https://www.openspaceproject.com):

- **2D**: one point per valid pixel, in the plane of the sky, with the measured surface density (`sigma`, g/cm²).
- **3D**: a constructed volume density (`rho`, g/cm³). Each radial profile from the star is inverse-Abel transformed
  with the pipeline's `do_abel_2`, then spun around the line of sight and sampled on a regular grid. The depth comes
  from the spherical-symmetry assumption, so the front and back halves are mirror images; projecting the cloud back
  along the line of sight gives the image again.

The asset places both clouds on Betelgeuse as OpenSpace draws it (Digital Universe stars catalog, with proper motion),
oriented on the sky, with color and size mapping options.

## Run

Needs Python 3 with numpy (2.x) and scipy. From the repository root:

```
python openspace/csm_openspace.py --out <output folder>
```

This writes `betelgeuse-csm-2d.csv`, `betelgeuse-csm-3d.csv` and `betelgeuse-csm.asset`. Copy the folder into OpenSpace's
user assets and add `betelgeuse-csm` from there. `python openspace/csm_openspace.py --help` lists the options (ray count,
grid spacing, density cutoff, sky orientation, distance).

`--check` recomputes the 3D densities with the settings of `coordinates_3d.ipynb` and compares them with
`saved_data/betelgeuse_csm_rho_and_coords_small_new.csv` (they agree to ~1e-13 relative).

## Differences from coordinates_3d.py / coordinates_3d.ipynb

- Ray angles are `2*pi*i/n_rays` with no duplicate ray at 2π. `coordinates_3d.py` used `(i/200)*2` radians, so all rays
  fell in a ~29° wedge; the notebook used `2*pi*i/51` for rays that are really `2*pi/50` apart (up to ~7° off).
- Rays stop just past the edge of the data instead of at 2.5".
- Points are on a uniform (jittered) grid instead of uniform (R, θ), which crowded points along the line of sight.
- The 3D cloud stops at the largest circle inside the square data crop (0.285"), and points below 1e-21 g/cm³ are
  dropped (`--to-corners`, `--min-rho` to change).

## Open item

The sky orientation assumes the usual ALMA layout (CDELT1 < 0: column index increases to the west; CDELT2 > 0: row
index increases to the north). The FITS header isn't in the repository; if it differs, use `--col-dir east` or
`--row-dir south`.

Note: in `interp_and_iat_2d.py`, `read_in_density_file` calls `start_abel(..., rnge, csm)` and `start_abel` calls
`regularization(..., csm, bkg)`, both with arguments in a different order than the signatures. The net effect is
`bkg = 0` in `regularization` (non-positive values and the inner 0.1" become 0, not the power-law floor). This script
reproduces that behavior so its results match the existing outputs.
