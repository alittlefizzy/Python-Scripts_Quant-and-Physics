
"""
4D visualisation in Manim: rotor-driven tesseracts.

    manim -pqh tesseract_4d.py TesseractRotations

Pipeline per frame
    1. 4D:   x  ->  R x R~            (rotor sandwich in Cl(4,0))
    2. 4->3: perspective from an eye on the e4 axis at w = eye_w
    3. 3->2: Manim's ThreeDCamera, exactly as for any 3D scene
"""
from __future__ import annotations

import itertools

import numpy as np
from manim import *
from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path



# =============================================================================
# Minimal Clifford algebra Cl(4,0) - just enough for rotors
# =============================================================================
_N = 4
_DIM = 1 << _N                           # 16 basis blades, indexed by bitmask
_VEC_IDX = [1 << i for i in range(_N)]   # blade indices of e1, e2, e3, e4


def _reorder_sign(a: int, b: int) -> float:
    """Sign picked up reordering the product of basis blades a, b (bitmasks)."""
    a >>= 1
    swaps = 0
    while a:
        swaps += bin(a & b).count("1")
        a >>= 1
    return -1.0 if swaps & 1 else 1.0


_BLADES = np.arange(_DIM)
_XOR = _BLADES[:, None] ^ _BLADES[None, :]
_SIGN = np.array([[_reorder_sign(a, b) for b in range(_DIM)] for a in range(_DIM)])
_OUTER_MASK = ((_BLADES[:, None] & _BLADES[None, :]) == 0).astype(float)
_GRADE = np.array([bin(a).count("1") for a in range(_DIM)])
_REVERSE_SIGN = (-1.0) ** (_GRADE * (_GRADE - 1) // 2)


class MV:
    """Multivector in Cl(4,0) (Euclidean metric, e_i^2 = +1).

    a * b   geometric product        a ^ b   outer (wedge) product
    ~a      reversion                a.norm()  sqrt of <a a~>_0
    """

    __slots__ = ("c",)

    def __init__(self, coeffs):
        self.c = np.asarray(coeffs, dtype=float)

    @classmethod
    def scalar(cls, s: float) -> "MV":
        c = np.zeros(_DIM)
        c[0] = s
        return cls(c)

    @classmethod
    def vector(cls, x) -> "MV":
        c = np.zeros(_DIM)
        c[_VEC_IDX] = x
        return cls(c)

    def _product(self, other: "MV", mask) -> "MV":
        out = np.zeros(_DIM)
        np.add.at(out, _XOR, np.outer(self.c, other.c) * _SIGN * mask)
        return MV(out)

    def __mul__(self, other):
        if isinstance(other, MV):
            return self._product(other, 1.0)
        return MV(self.c * other)

    def __rmul__(self, s):
        return MV(self.c * s)

    def __xor__(self, other: "MV") -> "MV":
        return self._product(other, _OUTER_MASK)

    def __add__(self, other):
        return MV(self.c + (other.c if isinstance(other, MV) else MV.scalar(other).c))

    __radd__ = __add__

    def __neg__(self):
        return MV(-self.c)

    def __sub__(self, other):
        return self + (-other)

    def __invert__(self) -> "MV":
        return MV(self.c * _REVERSE_SIGN)

    def grade(self, k: int) -> "MV":
        return MV(self.c * (_GRADE == k))

    def norm(self) -> float:
        return float(np.sqrt(self.c @ self.c))

    def as_vector(self) -> np.ndarray:
        return self.c[_VEC_IDX]


E1, E2, E3, E4 = (MV.vector(row) for row in np.eye(4))
BASIS = (E1, E2, E3, E4)


def exp_blade(B: MV) -> MV:
    """exp of a simple bivector (2-blade): B^2 = -|B|^2, so e^B = cos|B| + B^ sin|B|."""
    n = B.norm()
    if n < 1e-12:
        return MV.scalar(1.0)
    return MV.scalar(np.cos(n)) + B * (np.sin(n) / n)


def plane_rotor(B: MV, theta: float) -> MV:
    """R = exp(-B^ theta/2): rotation by theta in the plane of the 2-blade B,
    in the sense of B (for B = a ^ b, a turns towards b)."""
    return exp_blade(B * (-0.5 * theta / B.norm()))


def rotor_to_matrix(R: MV) -> np.ndarray:
    """The linear map x -> R x R~ as a 4x4 array (columns are the images of e_i).
    Built once per frame, so all vertices are moved by one numpy product."""
    R_rev = ~R
    return np.column_stack([(R * e * R_rev).as_vector() for e in BASIS])


def perspective_4d_to_3d(points4: np.ndarray, eye_w: float):
    """Project from an eye at w = eye_w on the e4 axis onto the hyperplane w = 0.
    Returns the 3D points and each point's w (its 4D depth)."""
    w = points4[:, 3]
    scale = eye_w / (eye_w - w)
    return points4[:, :3] * scale[:, None], w


# =============================================================================
# Manim layer
# =============================================================================
# Edges coloured by the axis they are parallel to at rest (e1, e2, e3, e4).
# Swap these for the project palette constants.
AXIS_COLOURS = [RED, GREEN, BLUE, YELLOW]


class Tesseract4D(VGroup):
    """A tesseract living in R^4. It stores a rotor; set_rotor(R) places it at
    R x R~ applied to the rest configuration and re-projects to 3D.

    4D depth is shown by stroke width and opacity: edges nearer the 4D eye
    (larger w) are drawn thicker and brighter.
    """

    def __init__(
        self,
        half_edge: float = 0.85,
        eye_w: float = 3.5,
        centre=ORIGIN,
        view_angle: float = 25 * DEGREES,
        stroke_width: float = 3.0,
        show_vertices: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.half_edge = half_edge
        self.eye_w = eye_w
        self.centre = np.array(centre, dtype=float)
        # Fixed 3D turn about the up axis so no faces sit edge-on to the camera.
        self.view_matrix = rotation_matrix(view_angle, OUT)
        self.base_width = stroke_width

        self.verts4 = half_edge * np.array(
            list(itertools.product((-1.0, 1.0), repeat=4))
        )
        self.edge_list = []
        for i, j in itertools.combinations(range(16), 2):
            differs = np.flatnonzero(self.verts4[i] != self.verts4[j])
            if len(differs) == 1:
                self.edge_list.append((i, j, int(differs[0])))

        self.edge_lines = VGroup(
            *[
                Line(ORIGIN, RIGHT, color=AXIS_COLOURS[axis], stroke_width=stroke_width)
                for *_, axis in self.edge_list
            ]
        )
        self.vertex_dots = VGroup(
            *[
                Dot3D(radius=0.04, color=WHITE, resolution=(6, 6))
                for _ in range(16)
            ]
            if show_vertices
            else []
        )
        self.add(self.edge_lines, self.vertex_dots)

        self.rotor = MV.scalar(1.0)
        self.set_rotor(self.rotor)

    def set_rotor(self, R: MV) -> "Tesseract4D":
        self.rotor = R
        P4 = self.verts4 @ rotor_to_matrix(R).T
        P3, w = perspective_4d_to_3d(P4, self.eye_w)
        P3 = P3 @ self.view_matrix.T + self.centre

        r = 2.0 * self.half_edge  # |vertex|, so w always lies in [-r, r]
        for line, (i, j, _) in zip(self.edge_lines, self.edge_list):
            line.set_points_as_corners(np.array([P3[i], P3[j]]))
            depth = 0.5 * (w[i] + w[j])
            nearness = (depth + r) / (2.0 * r)
            scale = self.eye_w / (self.eye_w - depth)
            line.set_stroke(width=self.base_width * scale, opacity=0.25 + 0.75 * nearness)
        if len(self.vertex_dots):
            for dot, p in zip(self.vertex_dots, P3):
                dot.move_to(p)
        return self


class FourDScene(ThreeDScene):
    """ThreeDScene for objects in R^4. Objects carry a rotor and project 4D -> 3D
    themselves; the inherited 3D camera does the final 3D -> 2D step.
    Camera: xy is the floor, z is up, x runs across the screen."""

    CAMERA_PHI = 70 * DEGREES
    CAMERA_THETA = -90 * DEGREES

    def setup(self):
        super().setup()
        self.set_camera_orientation(phi=self.CAMERA_PHI, theta=self.CAMERA_THETA)

    def rotate_4d(self, obj: Tesseract4D, rotor_of_t, **anim_kwargs) -> Animation:
        """Drive obj along rotor_of_t(t), t in [0, 1], composed on the left of its
        current rotor. Each frame is computed from the rest configuration,
        so no numerical drift accumulates."""
        R0 = obj.rotor
        return UpdateFromAlphaFunc(
            obj, lambda m, t: m.set_rotor(rotor_of_t(t) * R0), **anim_kwargs
        )


class TesseractRotations(FourDScene):
    # Rates for the double rotation. Equal rates = isoclinic (every point turns
    # by the same angle). Keep them integers so the loop closes at t = 1.
    OMEGA_1 = 1
    OMEGA_2 = 1

    def construct(self):
        simple = Tesseract4D(centre=[-3.5, 0, -0.4])
        double = Tesseract4D(centre=[3.5, 0, -0.4])

        B_simple = E1 ^ E4            # plane of x and w
        B_a, B_b = E1 ^ E2, E3 ^ E4   # floor plane and zw-plane: share only the origin

        left = VGroup(
            Tex(r"Simple rotation"),
            MathTex(r"R = e^{-e_1 e_4\,\theta/2}"),
            Tex(r"fixed plane: $e_2\wedge e_3$", font_size=30),
        ).arrange(DOWN, buff=0.15).scale(0.8).move_to([-3.5, 3.15, 0])
        right = VGroup(
            Tex(r"Double rotation"),
            MathTex(r"R = e^{-e_1 e_2\,\theta_1/2}\,e^{-e_3 e_4\,\theta_2/2}"),
            Tex(r"fixed: only the origin", font_size=30),
        ).arrange(DOWN, buff=0.15).scale(0.8).move_to([3.5, 3.15, 0])
        self.add_fixed_in_frame_mobjects(left, right)

        self.play(
            Create(simple.edge_lines),
            Create(double.edge_lines),
            FadeIn(simple.vertex_dots),
            FadeIn(double.vertex_dots),
            run_time=2,
        )
        self.wait(0.5)

        self.play(
            self.rotate_4d(simple, lambda t: plane_rotor(B_simple, TAU * t)),
            self.rotate_4d(
                double,
                lambda t: plane_rotor(B_a, self.OMEGA_1 * TAU * t)
                * plane_rotor(B_b, self.OMEGA_2 * TAU * t),
            ),
            run_time=12,
            rate_func=linear,
        )
        self.wait()
        


# --- Paste below FourDScene in tesseract_4d.py, and add to scene_map: ---
#         "SolidTesseract": SolidTesseractRotations,

# Fill colours for 4D depth, far from the 4D eye (w < 0) -> near (w > 0).
# Swap for the project palette constants.
FACE_FAR_COLOUR = BLUE
FACE_NEAR_COLOUR = GOLD


def tesseract_faces(verts4: np.ndarray) -> list[tuple[int, int, int, int]]:
    """The 24 square 2-faces as vertex-index quads in cyclic order. Each face is
    parallel to one of the 6 planes e_a ^ e_b, with the other two coordinates
    fixed at +-h: 6 planes x 4 sign choices."""
    index = {tuple(np.sign(v).astype(int)): k for k, v in enumerate(verts4)}
    faces = []
    for a, b in itertools.combinations(range(4), 2):
        c, d = (k for k in range(4) if k not in (a, b))
        for sc, sd in itertools.product((-1, 1), repeat=2):
            quad = []
            for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                s = [0, 0, 0, 0]
                s[a], s[b], s[c], s[d] = sa, sb, sc, sd
                quad.append(index[tuple(s)])
            faces.append(tuple(quad))
    return faces


class SolidTesseract4D(VGroup):
    """Tesseract drawn as its 24 square faces: translucent, lit panels that the
    3D camera depth-sorts every frame. Same interface as Tesseract4D (a stored
    rotor and set_rotor), so FourDScene.rotate_4d drives it unchanged.

    4D depth is shown by colour and opacity: faces nearer the 4D eye (larger w)
    are warmer and more transparent, since in projection they form the outer
    shell and would otherwise hide the far cell inside.
    """

    def __init__(
        self,
        half_edge: float = 0.85,
        eye_w: float = 3.5,
        centre=ORIGIN,
        view_angle: float = 25 * DEGREES,
        far_opacity: float = 0.40,
        near_opacity: float = 0.15,
        edge_width: float = 1.2,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.half_edge = half_edge
        self.eye_w = eye_w
        self.centre = np.array(centre, dtype=float)
        self.view_matrix = rotation_matrix(view_angle, OUT)
        self.far_opacity = far_opacity
        self.near_opacity = near_opacity

        self.verts4 = half_edge * np.array(
            list(itertools.product((-1.0, 1.0), repeat=4))
        )
        self.face_list = tesseract_faces(self.verts4)

        self.faces = VGroup(
            *[
                Polygon(
                    ORIGIN, RIGHT, UR, UP,
                    stroke_color=WHITE,
                    stroke_width=edge_width,
                    stroke_opacity=0.5,
                )
                for _ in self.face_list
            ]
        )
        for face in self.faces:
            face.set_shade_in_3d(True)  # lit, and depth-sorted by the 3D camera
        self.add(self.faces)

        self.rotor = MV.scalar(1.0)
        self.set_rotor(self.rotor)

    def set_rotor(self, R: MV) -> "SolidTesseract4D":
        self.rotor = R
        P4 = self.verts4 @ rotor_to_matrix(R).T
        P3, w = perspective_4d_to_3d(P4, self.eye_w)
        P3 = P3 @ self.view_matrix.T + self.centre

        r = np.sqrt(2.0) * self.half_edge  # |face centre|, so a face's mean w is in [-r, r]
        for face, quad in zip(self.faces, self.face_list):
            q = list(quad)
            face.set_points_as_corners(P3[q + q[:1]])
            nearness = (w[q].mean() + r) / (2.0 * r)
            face.set_fill(
                interpolate_color(FACE_FAR_COLOUR, FACE_NEAR_COLOUR, nearness),
                opacity=self.far_opacity + (self.near_opacity - self.far_opacity) * nearness,
            )
        return self


class SolidTesseractRotations(FourDScene):
    # Equal rates = isoclinic. Keep them integers so the loop closes at t = 1.
    OMEGA_1 = 1
    OMEGA_2 = 1

    def construct(self):
        simple = SolidTesseract4D(centre=[-3.5, 0, -0.4])
        double = SolidTesseract4D(centre=[3.5, 0, -0.4])

        B_simple = E1 ^ E4            # plane of x and w
        B_a, B_b = E1 ^ E2, E3 ^ E4   # floor plane and zw-plane: share only the origin

        left = VGroup(
            Tex(r"Simple rotation"),
            MathTex(r"R = e^{-e_1 e_4\,\theta/2}"),
            Tex(r"fixed plane: $e_2\wedge e_3$", font_size=30),
        ).arrange(DOWN, buff=0.15).scale(0.8).move_to([-3.5, 3.15, 0])
        right = VGroup(
            Tex(r"Double rotation"),
            MathTex(r"R = e^{-e_1 e_2\,\theta_1/2}\,e^{-e_3 e_4\,\theta_2/2}"),
            Tex(r"fixed: only the origin", font_size=30),
        ).arrange(DOWN, buff=0.15).scale(0.8).move_to([3.5, 3.15, 0])
        self.add_fixed_in_frame_mobjects(left, right)

        self.play(FadeIn(simple), FadeIn(double), run_time=2)
        self.wait(0.5)

        self.play(
            self.rotate_4d(simple, lambda t: plane_rotor(B_simple, TAU * t)),
            self.rotate_4d(
                double,
                lambda t: plane_rotor(B_a, self.OMEGA_1 * TAU * t)
                * plane_rotor(B_b, self.OMEGA_2 * TAU * t),
            ),
            run_time=12,
            rate_func=linear,
        )
        self.wait()
        
        
        
        
# --- Paste below SolidTesseract4D in tesseract_4d.py (it uses tesseract_faces,
# FACE_FAR_COLOUR and FACE_NEAR_COLOUR from there), and add to scene_map: ---
#         "OpaqueTesseract": OpaqueTesseractRotations,


def face_cells(verts4: np.ndarray, faces) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """For each square face, the two cells it lies in, as (axis, sign): the two
    coordinates that stay constant across the face."""
    cells = []
    for quad in faces:
        V = verts4[list(quad)]
        fixed = np.flatnonzero(np.all(V == V[0], axis=0))
        cells.append(tuple((int(k), int(np.sign(V[0, k]))) for k in fixed))
    return cells


def camera_position_getter(scene: ThreeDScene):
    """A callable giving the 3D camera's current position in scene coordinates.
    (A callable rather than the camera itself, so copying the mobject during
    animations doesn't try to copy the camera.)"""
    camera = scene.camera

    def position() -> np.ndarray:
        phi, theta = camera.get_phi(), camera.get_theta()
        direction = np.array(
            [np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)]
        )
        return np.array(camera.frame_center) + camera.get_focal_distance() * direction

    return position


class OpaqueTesseract4D(VGroup):
    """Opaque tesseract: only the outer surface of its 3D image is drawn.

    Seen from the 4D eye, each cell either faces it or faces away, exactly as
    the faces of a cube do when seen from a point. The outer surface of the
    projected image is made of the squares where a facing cell meets a
    turned-away cell (the 4D silhouette); every other square lies inside and
    is hidden. Same interface as Tesseract4D, so FourDScene.rotate_4d drives it.

    That surface is convex, so given the camera position it also drops the
    surface squares turned away from the camera. The remaining squares never
    overlap on screen, so no depth sorting is needed and none can go wrong.
    It re-checks every frame, so a moving camera is fine.
    """

    def __init__(
        self,
        half_edge: float = 0.85,
        eye_w: float = 3.5,
        centre=ORIGIN,
        view_angle: float = 25 * DEGREES,
        edge_colour=WHITE,
        edge_width: float = 1.5,
        edge_opacity: float = 0.6,
        camera_position=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.half_edge = half_edge
        self.eye_w = eye_w
        self.centre = np.array(centre, dtype=float)
        self.view_matrix = rotation_matrix(view_angle, OUT)
        self.edge_opacity = edge_opacity
        self.camera_position = camera_position

        self.verts4 = half_edge * np.array(
            list(itertools.product((-1.0, 1.0), repeat=4))
        )
        self.face_list = tesseract_faces(self.verts4)
        self.cells_of_face = face_cells(self.verts4, self.face_list)

        self.faces = VGroup(
            *[
                Polygon(
                    ORIGIN, RIGHT, UR, UP,
                    stroke_color=edge_colour,
                    stroke_width=edge_width,
                )
                for _ in self.face_list
            ]
        )
        for face in self.faces:
            face.set_shade_in_3d(True)  # lit, and depth-sorted by the 3D camera
        self.add(self.faces)

        self.rotor = MV.scalar(1.0)
        self.set_rotor(self.rotor)
        self.add_updater(lambda m: m.set_rotor(m.rotor))  # re-cull if the camera moves

    def set_rotor(self, R: MV) -> "OpaqueTesseract4D":
        self.rotor = R
        M = rotor_to_matrix(R)
        P4 = self.verts4 @ M.T
        P3, w = perspective_4d_to_3d(P4, self.eye_w)
        P3 = P3 @ self.view_matrix.T + self.centre

        # Cell (k, s) has outward normal n = R (s e_k) R~ = s M[:, k] and lies in
        # the hyperplane n.x = h. It faces the eye (0, 0, 0, d) when the eye is
        # on its outer side: n.eye = s M[3, k] d > h.
        facing = {
            (k, s): s * M[3, k] * self.eye_w > self.half_edge
            for k in range(4)
            for s in (-1, 1)
        }

        cam = self.camera_position() if self.camera_position else None
        middle = P3.mean(axis=0)  # inside the convex surface

        r = np.sqrt(2.0) * self.half_edge  # |face centre|, so a face's mean w is in [-r, r]
        for face, quad, (c1, c2) in zip(self.faces, self.face_list, self.cells_of_face):
            q = list(quad)
            corners = P3[q]
            face.set_points_as_corners(P3[q + q[:1]])

            visible = facing[c1] != facing[c2]
            if visible and cam is not None:
                normal = np.cross(corners[1] - corners[0], corners[3] - corners[0])
                centroid = corners.mean(axis=0)
                if np.dot(normal, centroid - middle) < 0:
                    normal = -normal  # make it point outward
                visible = np.dot(normal, cam - centroid) > 0

            nearness = (w[q].mean() + r) / (2.0 * r)
            face.set_fill(
                interpolate_color(FACE_FAR_COLOUR, FACE_NEAR_COLOUR, nearness),
                opacity=1.0 if visible else 0.0,
            )
            face.set_stroke(opacity=self.edge_opacity if visible else 0.0)
        return self


class OpaqueTesseractRotations(FourDScene):
    # Equal rates = isoclinic. Keep them integers so the loop closes at t = 1.
    OMEGA_1 = 1
    OMEGA_2 = 1

    def construct(self):
        cam = camera_position_getter(self)
        simple = OpaqueTesseract4D(centre=[-3.5, 0, -0.4], camera_position=cam)
        double = OpaqueTesseract4D(centre=[3.5, 0, -0.4], camera_position=cam)

        B_simple = E1 ^ E4            # plane of x and w
        B_a, B_b = E1 ^ E2, E3 ^ E4   # floor plane and zw-plane: share only the origin

        left = VGroup(
            Tex(r"Simple rotation"),
            MathTex(r"R = e^{-e_1 e_4\,\theta/2}"),
            Tex(r"fixed plane: $e_2\wedge e_3$", font_size=30),
        ).arrange(DOWN, buff=0.15).scale(0.8).move_to([-3.5, 3.15, 0])
        right = VGroup(
            Tex(r"Double rotation"),
            MathTex(r"R = e^{-e_1 e_2\,\theta_1/2}\,e^{-e_3 e_4\,\theta_2/2}"),
            Tex(r"fixed: only the origin", font_size=30),
        ).arrange(DOWN, buff=0.15).scale(0.8).move_to([3.5, 3.15, 0])
        self.add_fixed_in_frame_mobjects(left, right)

        self.play(FadeIn(simple), FadeIn(double), run_time=2)
        self.wait(0.5)

        self.play(
            self.rotate_4d(simple, lambda t: plane_rotor(B_simple, TAU * t)),
            self.rotate_4d(
                double,
                lambda t: plane_rotor(B_a, self.OMEGA_1 * TAU * t)
                * plane_rotor(B_b, self.OMEGA_2 * TAU * t),
            ),
            run_time=12,
            rate_func=linear,
        )
        self.wait()
        
        
        
        
if __name__ == "__main__":
    EXPORT_FINAL = True


    # Options: "all" or specific scene name(s) like "Scene2" or ["Scene1", "Scene2"]
    scenes_to_run = "Opaque Tesseract"

    export_path = Path(r"C:\Users\ambri\Downloads\A_Little_Fizzy\E2_The_Full_Geometric_Alg\Scenes")

    scene_map = {
        "Tesseract": TesseractRotations,
        "Solid Tesseract": SolidTesseractRotations,
        "Opaque Tesseract": OpaqueTesseractRotations,
    }

    # Resolve scene selection
    if scenes_to_run == "all":
        target_scenes = list(scene_map.keys())
    elif isinstance(scenes_to_run, list):
        target_scenes = scenes_to_run
    else:
        target_scenes = [scenes_to_run]

    if EXPORT_FINAL:
        # BATCH RENDER SPECIFIED SCENES TO MP4 (HIGH QUALITY)
        config.quality = "high_quality"
        config.preview = False
        config.write_to_movie = True
        config.video_dir = export_path

        for name in target_scenes:
            if name in scene_map:
                config.output_file = name
                scene_instance = scene_map[name]()
                scene_instance.render()
    else:
        # TEST MODE: PREVIEW FIRST TARGET SCENE
        target_scene = target_scenes[0]

        config.quality = "low_quality"
        config.preview = True
        config.write_to_movie = True  # Required for video player to launch
        config.output_file = f"{target_scene}_preview"

        scene_instance = scene_map[target_scene]()
        scene_instance.render()