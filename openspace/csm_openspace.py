#!/usr/bin/env python
"""Turn the Betelgeuse circumstellar-material (CSM) density map from csm_pipeline into two OpenSpace point clouds.

Source: the csm_pipeline repository (https://github.com/imanbeh/csm_pipeline), cloned one folder up. Its README says
the underlying ALMA data are not public, so the generated files are for internal use.

Input: ../saved_data/csm_2d_density.csv, a 1000 x 1000 surface-density image (g/cm^2) at 0.005"/pixel, centered on
pixel (col 499, row 499), NaN outside a 117 x 117 pixel square crop (0.29" to the sides, 0.41" to the corners). The
pipeline converts angles to parsecs at 168 pc.

Outputs (in --out):
  betelgeuse-csm-2d.csv  one point per valid pixel, in the plane of the sky (z = 0): the measured surface density.
  betelgeuse-csm-3d.csv  a 3D density cube that is *constructed*, not measured. As in the pipeline
                         (interp_and_iat_2d.py), the image is sampled along rays from the star at position angle psi,
                         and each ray's profile is inverse-Abel transformed into a volume density f_psi(R),
                         assuming spherical symmetry per ray. Here each ray's profile is then spun around the line
                         of sight: a point at 3D radius R and sky position angle psi gets rho = f_psi(R). Projecting
                         that field back along the line of sight gives back the image, but the depth structure is an
                         assumption (front and back are mirror images). The field is sampled on a regular, jittered
                         Cartesian grid so that the point density is uniform in space.
  betelgeuse-csm.asset   both clouds as RenderablePointCloud nodes, placed on Betelgeuse and oriented on the sky.

Differences from the pipeline's coordinates_3d.py / coordinates_3d.ipynb (which wrote
saved_data/betelgeuse_csm_rho_and_coords_small_new.csv):
  - ray angles are 2*pi*i/n_rays with no duplicate ray at 2*pi (the notebook used 2*pi*i/51 for rays that were really
    spaced 2*pi/50 apart, rotating them by up to 7 degrees; the .py used i/200*2 radians, a 29-degree wedge);
  - rays stop just past the edge of the data (her rays ran to 2.5", ~8x further than the data);
  - points are on a uniform grid instead of uniform (R, theta), which crowded points along the line of sight.
  The Abel transform itself is do_abel_2 from interp_and_iat_2d.py, reproduced unchanged (the module can't be imported
  without photutils and plotting side effects). Run with --check to compare against her exported CSV.

Placement: the node sits at Betelgeuse's position in the Digital Universe stars catalog that OpenSpace draws
(stars_du v7, HIP_27989: 152.67 pc, Hipparcos parallax), moved with the star's catalog velocity from J2000 the same way
the Stars layer moves it (UseProperMotion; ~175 au by 2026), so the cloud surrounds the star dot at any date between
1600 and 2400 (--no-proper-motion: fixed catalog position). Coordinates are
scaled to that distance so the cloud keeps the angular size of the ALMA image (all three axes; the depth is derived
from the same angular scale). Density values are left as the pipeline computes them at 168 pc. --no-rescale keeps
168 pc sizes.

Sky orientation: the FITS header isn't in the repository. The default assumes the usual ALMA/CASA layout, CDELT1 < 0
(column index increases to the west) and CDELT2 > 0 (row index increases to the north). Flip with --col-dir/--row-dir
once checked against the FITS header or a thesis figure.

Usage:
    python csm_openspace.py [--out DIR] [--rays 360] [--spacing 1.5] [--check]
"""
import argparse
import math
import shutil
from pathlib import Path

import numpy as np
from scipy.interpolate import RectBivariateSpline

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# --- pipeline constants (coordinates_3d.py / radial.py) ---
PIX_ARCSEC = 0.005
CENTER_COL, CENTER_ROW = 499, 499
MODEL_DISTANCE_PC = 168.0
ARCSEC_PER_RAD_PIPELINE = 206265.0  # radial.sm() uses 206265
MASK_ARCSEC = 0.1  # pipeline zeroes the star-subtracted core inside 0.1"
HER_RAY_STEP_PIX = 500.0 / 199.0  # her rays: np.linspace(0, cx + 1, 200) pixels

# --- placement ---
# Digital Universe stars.speck v7 (C:/OpenSpace/OpenSpaceData/sync/http/stars_du/7), row "HIP_27989 | ... | Betelgeuse":
# galactic x, y, z in parsecs, dist_ly 497.94865377.
BETELGEUSE_GAL_PC = np.array([-141.90495007, -51.05319468, -23.77435798])
# Same row, u v w (km/s, galactic). OpenSpace's Stars layer has UseProperMotion = true with ProperMotionEpoch 0 (J2000):
# star_vs.glsl draws each star at position + velocity * 1000 * (time - epoch), so by 2026 Betelgeuse is drawn ~175 au
# from its catalog position. The cloud follows the same straight line (see proper_motion_keyframes).
BETELGEUSE_UVW_KMS = np.array([-22.64007981, -10.84378577, 17.72124631])
MOTION_KEYFRAMES = ("1600-01-01T00:00:00", "2400-01-01T00:00:00")  # Gregorian, so datetime and SPICE agree
BETELGEUSE_RA, BETELGEUSE_DEC = 88.79293899, 7.40706399  # ICRS, SIMBAD; used only to check the catalog direction
PC_M = 3.0856775814913673e16
PC_CM = PC_M * 100.0
ICRS_TO_GAL = np.array([
    [-0.0548755604162154, -0.8734370902348850, -0.4838350155487132],
    [+0.4941094278755837, -0.4448296299600112, +0.7469822444972189],
    [-0.8676661490190047, -0.1980763734312015, +0.4559837761750669],
])

# Display defaults written into the asset, tuned live in OpenSpace (2026-11-20). ScaleExponent None = one grid spacing.
# Ranges: color range per parameter, overriding the one generated from the data.
DISPLAY = {
    "2d": {"Opacity": 0.5, "ScaleExponent": None, "SizeMappingEnabled": False, "SizeMappingScaleFactor": 1.0,
           "HideValuesOutsideRange": False, "Ranges": {}},
    "3d": {"Opacity": 0.01, "ScaleExponent": 10.4, "SizeMappingEnabled": True, "SizeMappingScaleFactor": 5.0,
           "HideValuesOutsideRange": True, "Ranges": {"log_rho": (-20.0108, -18.5808)}},
}

BASENAME = "betelgeuse-csm"
ID_2D, ID_3D = "BetelgeuseCSM2D", "BetelgeuseCSM3D"
GUI_PATH = "/Milky Way/Stars/Betelgeuse CSM"


def arcsec_to_cm(a, distance_pc=MODEL_DISTANCE_PC):
    return a * distance_pc / ARCSEC_PER_RAD_PIPELINE * PC_CM


def sample_rays(image, n_rays, n_pts, r_max_pix, endpoint=False):
    """Pipeline's ray_calculation: bicubic spline of the image (NaN -> 0), sampled along rays from the center.
    Returns psis (radians, measured from +column toward +row) and radii (pixels), and F[n_rays, n_pts]."""
    img = np.nan_to_num(image, nan=0.0)
    cols, rows = np.arange(img.shape[1], dtype=float), np.arange(img.shape[0], dtype=float)
    spline = RectBivariateSpline(cols, rows, img.T)  # spline(col, row) = image[row, col], as in the pipeline
    psis = np.linspace(0, 2 * np.pi, n_rays, endpoint=endpoint)
    rs = np.linspace(0, r_max_pix, n_pts)
    col = CENTER_COL + rs[None, :] * np.cos(psis)[:, None]
    row = CENTER_ROW + rs[None, :] * np.sin(psis)[:, None]
    return psis, rs, spline(col, row, grid=False)


def regularize(F, s_arcsec):
    """What the pipeline's regularization() step does as it is called in read_in_density_file (bkg ends up 0):
    values <= 0 and everything inside 0.1" become 0."""
    F = F.copy()
    F[F <= 0] = 0.0
    F[:, s_arcsec < MASK_ARCSEC] = 0.0
    return F


def do_abel_2(F_arr, s):
    """interp_and_iat_2d.do_abel_2, unchanged apart from returning r and f only.
    F: surface density along a ray; s: on-sky radius (cm), ascending. f[i] is the volume density at
    r = (s[i] + s[i+1]) / 2; the last entry is 0 (r is set to s[-1] there instead of the pipeline's 0)."""
    F = F_arr.copy()
    F[F < 0] = 0
    dF_ds = np.gradient(F, s)
    f_r = np.zeros(len(s))
    r_arr = np.zeros(len(s))
    for i in range(len(s) - 1):
        r = (s[i] + s[i + 1]) / 2
        r_arr[i] = r
        integ = np.trapezoid(dF_ds[i + 1:] / np.sqrt(s[s > r] ** 2 - r ** 2), s[s > r])
        f_r[i] = (-1 / np.pi) * integ
    r_arr[-1] = s[-1]
    return r_arr, f_r


def abel_rays(image, n_rays, n_pts, r_max_pix, endpoint=False):
    psis, rs, F = sample_rays(image, n_rays, n_pts, r_max_pix, endpoint)
    s_arc = rs * PIX_ARCSEC
    F = regularize(F, s_arc)
    s_cm = arcsec_to_cm(s_arc)
    f = np.zeros_like(F)
    for i in range(n_rays):
        r_cm, f[i] = do_abel_2(F[i], s_cm)
    r_arc = r_cm / arcsec_to_cm(1.0)
    return psis, r_arc, f


def eval_field(psis, r_arc, f, psi, R_arc):
    """rho at (position angle psi, 3D radius R): linear between neighbouring rays (periodic) and along the ray."""
    n = len(psis)
    k = (np.mod(psi, 2 * np.pi) / (2 * np.pi)) * n
    i0 = np.floor(k).astype(int) % n
    i1 = (i0 + 1) % n
    w = k - np.floor(k)
    j = np.interp(R_arc, r_arc, np.arange(len(r_arc)), right=np.nan)
    inside = ~np.isnan(j)
    j = np.where(inside, j, 0)
    j0 = np.clip(np.floor(j).astype(int), 0, len(r_arc) - 2)
    t = j - j0
    along = lambda i: f[i, j0] * (1 - t) + f[i, j0 + 1] * t
    out = along(i0) * (1 - w) + along(i1) * w
    out[~inside] = 0.0
    return out


def sky_frame():
    """Unit vectors (galactic) west, north, toward-observer at Betelgeuse's catalog position."""
    pos = BETELGEUSE_GAL_PC
    rhat = pos / np.linalg.norm(pos)
    ncp = ICRS_TO_GAL @ np.array([0.0, 0.0, 1.0])
    east = np.cross(ncp, rhat)
    east /= np.linalg.norm(east)
    north = np.cross(rhat, east)
    return pos, -east, north, -rhat


def proper_motion_keyframes():
    """{time string: position in meters} for a TimelineTranslation that reproduces the Stars layer's proper motion.
    Linear interpolation between two keyframes is exactly the shader's straight line. Seconds from J2000 are computed
    in UTC without leap seconds or TDB (~70 s, i.e. ~2000 km at 30 km/s: negligible)."""
    import datetime as dt
    j2000 = dt.datetime(2000, 1, 1, 12, 0, 0)
    out = {}
    for t in MOTION_KEYFRAMES:
        seconds = (dt.datetime.fromisoformat(t) - j2000).total_seconds()
        out[t] = BETELGEUSE_GAL_PC * PC_M + BETELGEUSE_UVW_KMS * 1000.0 * seconds
    return out


def euler_from_matrix(M):
    """Euler angles for OpenSpace's StaticRotation (glm::quat(euler), R = Rz(c) Ry(b) Rx(a))."""
    return np.array([math.atan2(M[2, 1], M[2, 2]), -math.asin(M[2, 0]), math.atan2(M[1, 0], M[0, 0])])


def matrix_from_euler(e):
    a, b, c = e
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


SIZE_RANGE = (0.4, 2.0)  # size-mapping factor range, times the base point size (as in the Crab asset)


def size_factor(value, lo, hi, sqrt=False):
    """Dimensionless point-size factor for OpenSpace's size mapping, which multiplies the column's raw value into the
    point size (raw sigma ~1e-4 or rho ~1e-19 would make every point vanish). value is clipped to lo..hi, optionally
    square-root stretched, and mapped to SIZE_RANGE; NaN (e.g. log of a non-positive value) gets the smallest size."""
    t = np.clip((np.nan_to_num(value, nan=lo) - lo) / (hi - lo), 0.0, 1.0)
    if sqrt:
        t = np.sqrt(t)
    return SIZE_RANGE[0] + (SIZE_RANGE[1] - SIZE_RANGE[0]) * t


def write_csv(path, header_lines, names, cols, fmts):
    with open(path, "w", encoding="utf8", newline="\n") as fh:
        for line in header_lines:
            fh.write(f"# {line}\n")
        fh.write(",".join(names) + "\n")
        rows = np.column_stack(cols)
        for r in rows:
            fh.write(",".join("" if np.isnan(v) else format(v, f) for v, f in zip(r, fmts)) + "\n")


def clear_openspace_cache(cache_dir, names):
    """OpenSpace caches datasets by path; drop the entries of regenerated files (best effort)."""
    for name in names:
        entry = Path(cache_dir) / name
        if entry.is_dir():
            shutil.rmtree(entry)
            print(f"cleared OpenSpace cache entry {entry}")


def check_against_notebook(image):
    """Recompute with the notebook's exact settings and compare with her exported CSV."""
    path = REPO / "saved_data" / "betelgeuse_csm_rho_and_coords_small_new.csv"
    n_l, n_p, n_z = 51, 200, 50
    psis, r_arc, f = abel_rays(image, n_l, n_p, CENTER_COL + 1, endpoint=True)
    her = np.loadtxt(path, delimiter=",", skiprows=1)
    rho_her = her[1::n_z, 3].reshape(n_l, n_p) / 1e24  # first theta sample of each (ray, point); row 0 is a dummy
    s_arc = np.linspace(0, CENTER_COL + 1, n_p) * PIX_ARCSEC
    mine = np.where(s_arc[None, :] > MASK_ARCSEC, f, 1e-99)
    mine[mine <= 0] = 1e-99
    ok = rho_her > 1e-90
    rel = np.abs(mine[ok] - rho_her[ok]) / np.abs(rho_her[ok]).max()
    print(f"--check: {ok.sum()} non-zero values, max |difference| / max(rho) = {rel.max():.2e}")
    return rel.max()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=REPO / "saved_data" / "csm_2d_density.csv")
    ap.add_argument("--out", type=Path, default=HERE / "output")
    ap.add_argument("--rays", type=int, default=360, help="number of rays (the notebook used 51)")
    ap.add_argument("--ray-step", type=float, default=HER_RAY_STEP_PIX,
                    help="sample spacing along each ray, pixels (default: the pipeline's 500/199)")
    ap.add_argument("--spacing", type=float, default=1.5, help="3D grid spacing, pixels (0.005\" each)")
    ap.add_argument("--no-jitter", action="store_true", help="don't jitter the 3D grid (jitter hides moire)")
    ap.add_argument("--min-rho", type=float, default=1e-21,
                    help="drop 3D points below this density, g/cm^3 (the signal is ~1e-20..2e-19; below that is "
                         "fringe from the crop edge and the spline)")
    ap.add_argument("--to-corners", action="store_true",
                    help="extend the 3D cloud to the corners of the square data crop (default: the largest circle "
                         "inside it, where every ray has data)")
    ap.add_argument("--col-dir", choices=["west", "east"], default="west",
                    help="sky direction of increasing column index (west if CDELT1 < 0, the ALMA default)")
    ap.add_argument("--row-dir", choices=["north", "south"], default="north",
                    help="sky direction of increasing row index (north if CDELT2 > 0)")
    ap.add_argument("--no-rescale", action="store_true",
                    help="size the cloud at the pipeline's 168 pc instead of the catalog distance")
    ap.add_argument("--no-proper-motion", action="store_true",
                    help="fixed catalog position instead of following the Stars layer's proper motion")
    ap.add_argument("--openspace-cache", type=Path, default=Path("C:/OpenSpace/OpenSpace/cache"))
    ap.add_argument("--check", action="store_true", help="compare against the notebook's exported CSV and exit")
    args = ap.parse_args()

    image = np.loadtxt(args.input, delimiter=",")
    if args.check:
        check_against_notebook(image)
        return

    pos, west, north, toward = sky_frame()
    cat_dist = float(np.linalg.norm(pos))
    radec = np.radians([BETELGEUSE_RA, BETELGEUSE_DEC])
    v = ICRS_TO_GAL @ np.array([math.cos(radec[1]) * math.cos(radec[0]),
                                math.cos(radec[1]) * math.sin(radec[0]), math.sin(radec[1])])
    sep = math.degrees(math.acos(np.clip(v @ (pos / cat_dist), -1, 1))) * 3600
    print(f"Betelgeuse in catalog: {cat_dist:.2f} pc, {sep:.2f}\" from its SIMBAD direction")
    place_dist = MODEL_DISTANCE_PC if args.no_rescale else cat_dist
    arc_to_pc = place_dist / ARCSEC_PER_RAD_PIPELINE
    sx = 1.0 if args.col_dir == "west" else -1.0  # CSV x = west
    sy = 1.0 if args.row_dir == "north" else -1.0  # CSV y = north

    # --- 2D: every valid pixel, in the sky plane ---
    valid = ~np.isnan(image)
    rows, cols = np.nonzero(valid)
    dx_arc = (cols - CENTER_COL) * PIX_ARCSEC
    dy_arc = (rows - CENTER_ROW) * PIX_ARCSEC
    r2_arc = np.hypot(dx_arc, dy_arc)
    sigma = image[rows, cols]
    log_sigma = np.where(sigma > 0, np.log10(np.where(sigma > 0, sigma, 1)), np.nan)
    r_data_arc = float(r2_arc.max())  # to the corners of the (square) crop
    nr, nc = np.nonzero(~valid)
    r_inner_arc = float(np.hypot(nc - CENTER_COL, nr - CENTER_ROW).min() - 1) * PIX_ARCSEC  # nearest NaN, minus 1 px
    r_cloud_arc = r_data_arc if args.to_corners else r_inner_arc

    # --- 3D: inverse Abel per ray, spun about the line of sight, sampled on a grid ---
    r_max_pix = r_data_arc / PIX_ARCSEC + 4 * args.ray_step  # a little past the edge so F reaches 0
    n_pts = int(round(r_max_pix / args.ray_step)) + 1
    psis, r_arc, f = abel_rays(image, args.rays, n_pts, r_max_pix)
    h = args.spacing * PIX_ARCSEC
    n = int(math.ceil(r_cloud_arc / h))
    ax = np.arange(-n, n + 1) * h
    X, Y, Z = (a.ravel() for a in np.meshgrid(ax, ax, ax, indexing="ij"))
    if not args.no_jitter:
        rng = np.random.default_rng(27989)
        X, Y, Z = (a + rng.uniform(-h / 2, h / 2, a.shape) for a in (X, Y, Z))
    R = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
    keep = (R >= MASK_ARCSEC) & (R <= r_cloud_arc)
    X, Y, Z, R = X[keep], Y[keep], Z[keep], R[keep]
    rho = eval_field(psis, r_arc, f, np.arctan2(Y, X), R)  # X, Y in image col/row directions
    pos_rho = rho >= args.min_rho
    print(f"3D: {keep.sum()} grid points in the shell {MASK_ARCSEC}\"-{r_cloud_arc:.3f}\", "
          f"{pos_rho.sum()} with rho >= {args.min_rho:g} kept, {(~pos_rho).sum()} dropped")
    X, Y, Z, R, rho = X[pos_rho], Y[pos_rho], Z[pos_rho], R[pos_rho], rho[pos_rho]
    log_rho = np.log10(rho)

    # Color ranges, and size factors over the same ranges: sigma over its linear color range (square-root stretched,
    # like the Crab's flux_size), rho over its log color range (it spans ~1.3 decades, so linear rho would leave
    # nearly every point at the minimum size).
    SIGMA_RANGE = (0.0, 2e-4)  # the pipeline's vmax_gcm2
    ls_lo, ls_hi = np.nanpercentile(log_sigma, [5, 99.5])
    lr_lo, lr_hi = np.percentile(log_rho, [5, 99.5])
    sigma_size = size_factor(sigma, *SIGMA_RANGE, sqrt=True)
    rho_size = size_factor(log_rho, lr_lo, lr_hi)

    au = lambda a: a * place_dist  # 1" at d pc = d au
    args.out.mkdir(parents=True, exist_ok=True)
    common = [
        "Betelgeuse circumstellar material, from csm_pipeline (github.com/imanbeh/csm_pipeline); ALMA data not public.",
        f"x = west, y = north, z = toward observer, parsecs from Betelgeuse, sized for {place_dist:.2f} pc "
        f"(column index -> {args.col_dir}, row index -> {args.row_dir}).",
    ]
    csv2 = f"{BASENAME}-2d.csv"
    write_csv(args.out / csv2, common + [
        "2D: measured surface density in the plane of the sky (z = 0). sigma g/cm^2 (negative = over-subtracted",
        "star residual), log_sigma = log10(sigma) (blank where sigma <= 0), r_au = projected radius in au.",
        f"sigma_size: point-size factor {SIZE_RANGE[0]}-{SIZE_RANGE[1]}, sqrt of sigma over {SIGMA_RANGE[0]:g}-"
        f"{SIGMA_RANGE[1]:g} (not a measurement)."],
        ["x", "y", "z", "sigma", "log_sigma", "r_au", "sigma_size"],
        [sx * dx_arc * arc_to_pc, sy * dy_arc * arc_to_pc, np.zeros_like(dx_arc), sigma, log_sigma, au(r2_arc),
         sigma_size],
        [".6e", ".6e", ".1f", ".6e", ".5f", ".4f", ".4f"])
    csv3 = f"{BASENAME}-3d.csv"
    write_csv(args.out / csv3, common + [
        "3D: CONSTRUCTED volume density. Inverse Abel transform per ray (pipeline's do_abel_2), spun about the line",
        "of sight; front and back are mirror images. rho g/cm^3 (computed at 168 pc), log_rho = log10(rho),",
        f"r_au = 3D radius in au. {args.rays} rays, grid spacing {args.spacing} px, shell {MASK_ARCSEC}\"-"
        f"{r_cloud_arc:.3f}\", rho >= {args.min_rho:g}.",
        f"rho_size: point-size factor {SIZE_RANGE[0]}-{SIZE_RANGE[1]}, linear in log_rho over {lr_lo:.2f}-{lr_hi:.2f} "
        "(not a measurement)."],
        ["x", "y", "z", "rho", "log_rho", "r_au", "rho_size"],
        [sx * X * arc_to_pc, sy * Y * arc_to_pc, Z * arc_to_pc, rho, log_rho, au(R), rho_size],
        [".6e", ".6e", ".6e", ".6e", ".5f", ".4f", ".4f"])
    clear_openspace_cache(args.openspace_cache, [csv2, csv3])

    # --- asset ---
    M = np.column_stack([west, north, toward])
    assert abs(np.linalg.det(M) - 1) < 1e-9
    euler = euler_from_matrix(M)
    assert np.allclose(matrix_from_euler(euler), M, atol=1e-9)
    p = pos * PC_M
    spacing_m_2d = PIX_ARCSEC * arc_to_pc * PC_M
    spacing_m_3d = h * arc_to_pc * PC_M
    fmt3 = lambda v, k="": "{ " + ", ".join(f"{c:.9f}{k}" for c in v) + " }"
    view_dist_m = 4 * r_data_arc * arc_to_pc * PC_M
    pos_lua = lambda q: f"{{ {q[0]:.12e}, {q[1]:.12e}, {q[2]:.12e} }}"
    if args.no_proper_motion:
        translation_lua = (
            "-- Betelgeuse in the Digital Universe stars catalog (stars_du v7, HIP_27989), meters, galactic.\n"
            f'local Translation = {{ Type = "StaticTranslation", Position = {pos_lua(p)} }}')
    else:
        frames = proper_motion_keyframes()
        kf = ",\n".join(f'    ["{t}"] = {{ Type = "StaticTranslation", Position = {pos_lua(q)} }}'
                        for t, q in frames.items())
        translation_lua = f"""-- Betelgeuse in the Digital Universe stars catalog (stars_du v7, HIP_27989), meters, galactic, moved the way the
-- Stars layer moves it (UseProperMotion, epoch J2000): catalog position + (u, v, w) km/s * (time - J2000). Linear
-- interpolation between these two keyframes is that straight line; outside {MOTION_KEYFRAMES[0][:4]}-{MOTION_KEYFRAMES[1][:4]} the cloud stops
-- at the end keyframe. If the Stars layer's UseProperMotion is turned off, the star jumps back to its catalog
-- position (~175 au away in 2026); regenerate with --no-proper-motion to match that.
local Translation = {{
  Type = "TimelineTranslation",
  Keyframes = {{
{kf}
  }}
}}"""

    def node(ident, name, csv, params, default, spacing_m, enabled, display, size_key, size_what):
        params = [(k, display["Ranges"].get(k, rng)) for k, rng in params]
        opts = ",\n".join(f'          {{ Key = "{k}", Range = {{ {lo:.6g}, {hi:.6g} }} }}' for k, (lo, hi) in params)
        opacity = display["Opacity"]
        exponent = display["ScaleExponent"] if display["ScaleExponent"] is not None else math.log10(spacing_m)
        exponent_note = ("tuned live" if display["ScaleExponent"] is not None
                         else "10^this m = one grid spacing")
        return f"""local {ident} = {{
  Identifier = "{ident}",
  Parent = "Root",
  -- Without these the camera can't get closer than ~5 pc to the node (the cloud is ~60 au across).
  InteractionSphere = {spacing_m:.3e},
  BoundingSphere = {2 * r_data_arc * arc_to_pc * PC_M:.3e},
  Transform = {{
    Translation = Translation,
    Rotation = {{ Type = "StaticRotation", Rotation = Rotation }}
  }},
  Renderable = {{
    Type = "RenderablePointCloud",
    Enabled = {str(enabled).lower()},
    File = asset.resource("{csv}"),
    UseCaching = false,  -- reread the CSV on every load while the data is still changing
    Unit = "pc",
    Texture = {{ Enabled = false }},
    Opacity = {opacity},  -- points blend additively; the 3D cloud saturates to white above ~0.05
    Coloring = {{
      ColorMapping = {{
        File = colormaps.Uniform.Inferno,
        ParameterOptions = {{
{opts}
        }},
        Parameter = "{default}",
        HideValuesOutsideRange = {str(display["HideValuesOutsideRange"]).lower()},
        ShowMissingData = false
      }}
    }},
    SizeSettings = {{
      -- Scale each point by {size_what} ({size_key}: {SIZE_RANGE[0]}x to {SIZE_RANGE[1]}x, times ScaleFactor below).
      -- Toggle in the GUI under Sizing > Size Mapping.
      SizeMapping = {{
        Enabled = {str(display["SizeMappingEnabled"]).lower()},
        ParameterOptions = {{ "{size_key}" }},
        Parameter = "{size_key}",
        ScaleFactor = {display["SizeMappingScaleFactor"]}
      }},
      ScaleFactor = 1.0,
      ScaleExponent = {exponent:.2f}  -- {exponent_note}
    }}
  }},
  GUI = {{
    Name = "{name}",
    Path = "{GUI_PATH}",
    Description = Description
  }}
}}
"""

    asset = f"""-- Betelgeuse circumstellar material (CSM) from ALMA, two point clouds.
-- Generated by csm_openspace.py (csm-import/openspace); data from csm_pipeline, github.com/imanbeh/csm_pipeline.
-- The ALMA data behind it are not public: internal use.
local colormaps = asset.require("util/default_colormaps")

local Description = [[Circumstellar material around Betelgeuse from ALMA continuum imaging (csm_pipeline). The 2D
  cloud is the measured surface density (g/cm^2) in the plane of the sky. The 3D cloud is constructed, not measured: each
  radial profile from the star was inverse-Abel transformed into a volume density (g/cm^3) assuming spherical
  symmetry, then spun around the line of sight, so its depth structure is an assumption and its front and back are mirror
  images. Placed on Betelgeuse at {place_dist:.1f} pc (Digital Universe stars), sized to the angular size of the ALMA
  image; the star-subtracted core inside {MASK_ARCSEC} arcsec is left out. Up close the Betelgeuse star sprite covers
  the clouds: turn off the Stars layer to see them.]]

{translation_lua}
-- CSV frame (x = west, y = north, z = toward observer) -> galactic; Euler radians, R = Rz * Ry * Rx.
local Rotation = {{ {euler[0]:.9f}, {euler[1]:.9f}, {euler[2]:.9f} }}

{node(ID_2D, "Betelgeuse CSM 2D (sky plane)", csv2,
      [("sigma", SIGMA_RANGE), ("log_sigma", (ls_lo, ls_hi)), ("r_au", (0.0, au(r_data_arc)))],
      "sigma", spacing_m_2d, True, DISPLAY["2d"], "sigma_size", "surface density")}
{node(ID_3D, "Betelgeuse CSM 3D (Abel model)", csv3,
      [("log_rho", (lr_lo, lr_hi)), ("rho", (0.0, float(np.percentile(rho, 99.5)))), ("r_au", (0.0, au(r_cloud_arc)))],
      "log_rho", spacing_m_3d, False, DISPLAY["3d"], "rho_size", "volume density")}
-- Anchor the camera on the cloud, on the Earth side, north up (east is then on the left, as on the sky).
local orientFromEarth = {{
  Identifier = "betelgeuse_csm.orient_from_earth",
  Name = "Orient view from Earth",
  GuiPath = "{GUI_PATH}",
  IsLocal = true,
  Command = [[
    openspace.navigation.setNavigationState({{
      Anchor = "{ID_2D}",
      ReferenceFrame = "Root",
      Position = {fmt3(toward * view_dist_m)},
      Up = {fmt3(north)},
      Yaw = 0.0,
      Pitch = 0.0
    }})
  ]]
}}

asset.onInitialize(function()
  openspace.addSceneGraphNode({ID_2D})
  openspace.addSceneGraphNode({ID_3D})
  openspace.action.registerAction(orientFromEarth)
end)
asset.onDeinitialize(function()
  openspace.action.removeAction(orientFromEarth.Identifier)
  openspace.removeSceneGraphNode({ID_3D})
  openspace.removeSceneGraphNode({ID_2D})
end)

asset.export({ID_2D})
asset.export({ID_3D})

asset.meta = {{
  Name = "Betelgeuse CSM (2D and 3D)",
  Description = Description,
  Author = "Data: csm_pipeline (github.com/imanbeh/csm_pipeline). Asset: csm_openspace.py",
  URL = "https://github.com/imanbeh/csm_pipeline",
  License = "Internal use; the ALMA data are not public"
}}
"""
    (args.out / f"{BASENAME}.asset").write_text(asset, encoding="utf8")
    print(f"2D: {len(sigma)} points; 3D: {len(rho)} points; rays {args.rays} x {n_pts} to {r_max_pix:.1f} px")
    print(f"log_sigma range {ls_lo:.2f}..{ls_hi:.2f}, log_rho range {lr_lo:.2f}..{lr_hi:.2f}")
    print(f"2D to {au(r_data_arc):.1f} au (corners), 3D to {au(r_cloud_arc):.1f} au, at {place_dist:.2f} pc; "
          f"wrote {args.out}")


if __name__ == "__main__":
    main()
