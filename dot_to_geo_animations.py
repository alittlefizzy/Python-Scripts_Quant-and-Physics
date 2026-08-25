from manim import *
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path
import random






def create_hazy_line(
    start_pt, 
    end_pt, 
    color=PINK, 
    core_width=0.05, 
    glow_radius=0.40, 
    num_layers=30, 
    opacity=1.0  # Controls total opacity (0.0 to 1.0)
):
    """
    Creates a hazy, emitting light footprint along a vector segment 
    using concentric rounded hulls with configurable overall opacity.
    """
    glow_group = VGroup()
    vec = end_pt - start_pt
    length = np.linalg.norm(vec)
    angle = np.arctan2(vec[1], vec[0])
    center = (start_pt + end_pt) / 2.0

    for i in range(num_layers, 0, -1):
        progress = i / num_layers
        current_radius = core_width + (glow_radius - core_width) * (progress ** 1.5)
        
        # Base layer opacity scaled directly by the opacity argument
        layer_opacity = (0.015 + 0.08 * ((1.0 - progress) ** 2)) * opacity

        layer = RoundedRectangle(
            corner_radius=current_radius / 2,
            height=current_radius,
            width=length + current_radius,
            stroke_width=0,
            fill_color=color,
            fill_opacity=layer_opacity
        )
        layer.rotate(angle)
        layer.move_to(center)
        glow_group.add(layer)

    # Core lines scaled by the opacity argument as well
    core = Line(start_pt, end_pt, color=WHITE, stroke_width=2.5).set_opacity(0.85 * opacity)
    primary = Line(start_pt, end_pt, color=color, stroke_width=4.0).set_opacity(0.60 * opacity)
    
    glow_group.add(primary, core)
    return glow_group


class Scene1(Scene):
    def construct(self):
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"

        # ----------------------------------------------------
        # Top Header & Diagram (t = 0.00s)
        # ----------------------------------------------------
        top_eq = MathTex(
            r"\vec{a} \cdot \vec{b} = a b \cos\theta = a_x b_x + a_y b_y + a_z b_z",
            color=WHITE
        ).scale(0.85).move_to(LEFT * 3.2 + UP * 2.2)

        diag_offset = RIGHT * 2.5 + UP * 1.5

        vec_b = Arrow(ORIGIN, RIGHT * 3.5, color=PURPLE_COLOR, buff=0).shift(diag_offset)
        vec_a = Arrow(ORIGIN, RIGHT * 2.2 + UP * 1.3, color=PINK_COLOR, buff=0).shift(diag_offset)

        proj_point = diag_offset + RIGHT * 2.2
        proj_line = DashedLine(vec_a.get_end(), proj_point, color=GRAY)

        shadow_glow = create_hazy_line(
            start_pt=diag_offset,
            end_pt=proj_point,
            color=PINK_COLOR,
            core_width=0.05,
            glow_radius=0.40,
            num_layers=30,
            opacity=1.0
        )

        angle = Angle(vec_b, vec_a, radius=0.7, color=BLUE_COLOR)
        angle_label = MathTex(r"\theta", color=BLUE_COLOR).scale(0.8).next_to(angle, RIGHT, buff=0.1).shift(UP * 0.1)

        label_b = MathTex(r"\vec{b}", color=PURPLE_COLOR).scale(0.9).next_to(vec_b.get_end(), DOWN * 0.4 + RIGHT * 0.1)
        label_a = MathTex(r"\vec{a}", color=PINK_COLOR).scale(0.9).next_to(vec_a.get_end(), UP * 0.2)

        self.add(top_eq, shadow_glow, vec_b, vec_a, proj_line, angle, angle_label, label_b, label_a)

        # Pause until t = 5s 02f (5.033s at 60 fps)
        self.wait(5 + 2/60)

        # ----------------------------------------------------
        # Derivation Section
        # ----------------------------------------------------
        
        # Line 1: Starts at t = 5.033s, ends at t = 6.033s
        eq1 = MathTex(r"\vec{a}", r"\cdot", r"(\vec{b} + \vec{c})").move_to(UP * 0.25)
        self.play(Write(eq1), run_time=1.0)
        self.wait(0.9)  # t = 6.933s

        # Line 2: Ends at t = 8.933s
        eq2 = MathTex(
            r"=", 
            r"(", r"{{a_x \hat{x}}}", r"+", r"{{a_y \hat{y}}}", r"+", r"{{a_z \hat{z}}}", r")", 
            r"\cdot", 
            r"[", r"{{(b_x + c_x)\hat{x}}}", r"+", r"{{(b_y + c_y)\hat{y}}}", r"+", r"{{(b_z + c_z)\hat{z}}}", r"]"
        ).scale(0.72).next_to(eq1, DOWN, buff=0.22)

        self.play(
            Write(eq2[0]), Write(eq2[1]), Write(eq2[3]), Write(eq2[5]), Write(eq2[7]),
            Write(eq2[8]), Write(eq2[9]), Write(eq2[11]), Write(eq2[13]), Write(eq2[15]),
            TransformFromCopy(eq1[0], eq2[2]),
            TransformFromCopy(eq1[0], eq2[4]),
            TransformFromCopy(eq1[0], eq2[6]),
            TransformFromCopy(eq1[2], eq2[10]),
            TransformFromCopy(eq1[2], eq2[12]),
            TransformFromCopy(eq1[2], eq2[14]),
            run_time=2.0
        )
        self.wait(0.9)  # t = 9.833s

        # Line 3: Ends at t = 12.833s
        eq3 = MathTex(
            r"=", 
            r"{{a_x(b_x + c_x)}}", 
            r"+", 
            r"{{a_y(b_y + c_y)}}", 
            r"+", 
            r"{{a_z(b_z + c_z)}}"
        ).scale(0.75).next_to(eq2, DOWN, buff=0.22)

        self.play(
            Write(eq3[0]),
            ReplacementTransform(eq2[2].copy(), eq3[1]),
            ReplacementTransform(eq2[10].copy(), eq3[1]),
            run_time=1.0
        )
        self.play(
            Write(eq3[2]),
            ReplacementTransform(eq2[4].copy(), eq3[3]),
            ReplacementTransform(eq2[12].copy(), eq3[3]),
            run_time=1.0
        )
        self.play(
            Write(eq3[4]),
            ReplacementTransform(eq2[6].copy(), eq3[5]),
            ReplacementTransform(eq2[14].copy(), eq3[5]),
            run_time=1.0
        )
        self.wait(0.9)  # t = 13.733s

        # Line 4: Ends at t = 17.333s
        eq4 = MathTex(
            r"=", 
            r"(", r"{{a_x b_x}}", r"+", r"{{a_y b_y}}", r"+", r"{{a_z b_z}}", r")", 
            r"+", 
            r"(", r"{{a_x c_x}}", r"+", r"{{a_y c_y}}", r"+", r"{{a_z c_z}}", r")"
        ).scale(0.72).next_to(eq3, DOWN, buff=0.22)

        self.play(
            Write(eq4[0]), Write(eq4[1]), Write(eq4[7]), Write(eq4[8]), Write(eq4[9]), Write(eq4[15]),
            TransformFromCopy(eq3[1], eq4[2]),
            TransformFromCopy(eq3[1], eq4[10]),
            run_time=1.2
        )
        self.play(
            Write(eq4[3]), Write(eq4[11]),
            TransformFromCopy(eq3[3], eq4[4]),
            TransformFromCopy(eq3[3], eq4[12]),
            run_time=1.2
        )
        self.play(
            Write(eq4[5]), Write(eq4[13]),
            TransformFromCopy(eq3[5], eq4[6]),
            TransformFromCopy(eq3[5], eq4[14]),
            run_time=1.2
        )
        self.wait(0.9)  # t = 18.233s

        # Line 5: Ends precisely at t = 20s 22f (20.367s)
        eq5 = MathTex(
            r"=", 
            r"\vec{a} \cdot \vec{b}", 
            r"+", 
            r"\vec{a} \cdot \vec{c}"
        ).next_to(eq4, DOWN, buff=0.22)

        self.play(
            Write(eq5[0]),
            ReplacementTransform(VGroup(eq4[2], eq4[4], eq4[6]).copy(), eq5[1]),
            run_time=1.0
        )
        self.play(
            Write(eq5[2]),
            ReplacementTransform(VGroup(eq4[10], eq4[12], eq4[14]).copy(), eq5[3]),
            run_time=1 + 8/60
        )
        
        # Hold frame after computation completes
        self.wait(3.0)

        
class Scene2(Scene):
    def construct(self):
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"
        RED_COLOR = "#FF5555"
        GREEN_COLOR = "#50FA7B"
        BRIGHT_YELLOW = "#FFFF00"

        # ----------------------------------------------------
        # Recreate Scene 1 Final Frame Exactly
        # ----------------------------------------------------
        top_eq = MathTex(
            r"\vec{a} \cdot \vec{b} = a b \cos\theta = a_x b_x + a_y b_y + a_z b_z",
            color=WHITE
        ).scale(0.85).move_to(LEFT * 3.2 + UP * 2.2)

        diag_offset = RIGHT * 2.5 + UP * 1.5

        vec_b = Arrow(ORIGIN, RIGHT * 3.5, color=PURPLE_COLOR, buff=0).shift(diag_offset)
        vec_a = Arrow(ORIGIN, RIGHT * 2.2 + UP * 1.3, color=PINK_COLOR, buff=0).shift(diag_offset)

        proj_point = diag_offset + RIGHT * 2.2
        proj_line = DashedLine(vec_a.get_end(), proj_point, color=GRAY)

        shadow_glow = create_hazy_line(
            start_pt=diag_offset,
            end_pt=proj_point,
            color=PINK_COLOR,
            core_width=0.05,
            glow_radius=0.40,
            num_layers=30,
            opacity=1.0
        )

        angle = Angle(vec_b, vec_a, radius=0.7, color=BLUE_COLOR)
        angle_label = MathTex(r"\theta", color=BLUE_COLOR).scale(0.8).next_to(angle, RIGHT, buff=0.1).shift(UP * 0.1)

        label_b = MathTex(r"\vec{b}", color=PURPLE_COLOR).scale(0.9).next_to(vec_b.get_end(), DOWN * 0.4 + RIGHT * 0.1)
        label_a = MathTex(r"\vec{a}", color=PINK_COLOR).scale(0.9).next_to(vec_a.get_end(), UP * 0.2)

        eq1 = MathTex(
            r"\vec{a}", r"\cdot", r"(", r"\vec{b}", r"+", r"\vec{c}", r")"
        ).move_to(UP * 0.25)

        eq2 = MathTex(
            r"=", 
            r"(", r"{{a_x \hat{x}}}", r"+", r"{{a_y \hat{y}}}", r"+", r"{{a_z \hat{z}}}", r")", 
            r"\cdot", 
            r"[", r"{{(b_x + c_x)\hat{x}}}", r"+", r"{{(b_y + c_y)\hat{y}}}", r"+", r"{{(b_z + c_z)\hat{z}}}", r"]"
        ).scale(0.72).next_to(eq1, DOWN, buff=0.22)

        eq3 = MathTex(
            r"=", 
            r"{{a_x(b_x + c_x)}}", 
            r"+", 
            r"{{a_y(b_y + c_y)}}", 
            r"+", 
            r"{{a_z(b_z + c_z)}}"
        ).scale(0.75).next_to(eq2, DOWN, buff=0.22)

        eq4 = MathTex(
            r"=", 
            r"(", r"{{a_x b_x}}", r"+", r"{{a_y b_y}}", r"+", r"{{a_z b_z}}", r")", 
            r"+", 
            r"(", r"{{a_x c_x}}", r"+", r"{{a_y c_y}}", r"+", r"{{a_z c_z}}", r")"
        ).scale(0.72).next_to(eq3, DOWN, buff=0.22)

        eq5 = MathTex(
            r"=", 
            r"\vec{a} \cdot \vec{b}", 
            r"+", 
            r"\vec{a} \cdot \vec{c}"
        ).next_to(eq4, DOWN, buff=0.22)

        self.add(
            top_eq, shadow_glow, vec_b, vec_a, proj_line, angle, angle_label, label_b, label_a,
            eq1, eq2, eq3, eq4, eq5
        )

        # ----------------------------------------------------
        # Timeline Alignment (Start: 23:00 -> t = 0.00s)
        # ----------------------------------------------------
        self.wait(2.20)

        # t = 2.20s (25:06 on timeline): Erase text simultaneously left to right
        calculations = VGroup(eq2, eq3, eq4, eq5)
        all_chars = [
            char for eq in calculations 
            for char in eq.get_family() 
            if len(char.points) > 0 and not char.submobjects
        ]
        all_chars.sort(key=lambda c: c.get_center()[0])

        self.play(
            LaggedStart(
                *[FadeOut(char, run_time=0.15) for char in all_chars],
                lag_ratio=1.0 / len(all_chars)
            ),
            run_time=0.8
        )
        self.remove(calculations)

        # Plus sign morphs into dot
        dot_symbol = MathTex(r"\cdot", color=BRIGHT_YELLOW).scale(1.4).move_to(eq1[4].get_center())
        self.play(
            eq1[4].animate.set_color(BRIGHT_YELLOW).scale(1.4),
            run_time=0.2
        )
        self.play(
            Transform(eq1[4], dot_symbol),
            run_time=0.4
        )
        self.play(
            eq1[4].animate.set_color(WHITE).scale(1 / 1.4),
            run_time=0.2
        )
        self.wait(0.20)

        # t = 4.00s (27:00 on timeline): Equals and Question Marks appear
        equals_sign = MathTex(r"=", color=WHITE).next_to(eq1, RIGHT, buff=0.25)
        question_marks = MathTex(r"?", r"?", r"?", color=BRIGHT_YELLOW).next_to(equals_sign, RIGHT, buff=0.2)

        self.play(Write(equals_sign), run_time=0.3)
        self.play(Write(question_marks), run_time=0.5)
        self.wait(1.57)

        # t = 6.37s (29:11 on timeline): "scalar" label appears
        bc_group = VGroup(eq1[3], eq1[4], eq1[5])
        brace_bc = Brace(bc_group, direction=DOWN, color=RED_COLOR)
        label_scalar = MathTex(r"\text{scalar}", color=RED_COLOR).scale(0.85).next_to(brace_bc, DOWN, buff=0.15)

        self.play(
            GrowFromCenter(brace_bc),
            Write(label_scalar),
            run_time=0.6
        )
        self.wait(0.77)

        # t = 7.73s (30:22 on timeline): "vector" label appears
        brace_a = Brace(eq1[0], direction=DOWN, color=GREEN_COLOR)
        label_vector = MathTex(r"\text{vector}", color=GREEN_COLOR).scale(0.85).next_to(brace_a, DOWN, buff=0.15)

        self.play(
            GrowFromCenter(brace_a),
            Write(label_vector),
            run_time=0.6
        )

        # t = 8.33s -> hold until 11.53s (34:16 on timeline)
        self.wait(5.00)


def create_chain_bar(length, color, height=0.25):
    rect = RoundedRectangle(
        corner_radius=0.1, height=height, width=length, color=color, fill_opacity=0.25
    )
    num_links = max(2, int(length / 0.35))
    links = VGroup()
    for i in range(num_links):
        link_w = length / num_links
        link = RoundedRectangle(
            corner_radius=0.06, height=height * 0.75, width=link_w, color=color
        )
        link.move_to(rect.get_left() + RIGHT * (i + 0.5) * link_w)
        links.add(link)
    return VGroup(rect, links)


class Scene3(Scene):
    def construct(self):
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"
        RED_COLOR = "#FF5555"
        GREEN_COLOR = "#50FA7B"
        BRIGHT_YELLOW = "#FFFF00"

        # ----------------------------------------------------
        # Recreate Scene 2 Final Frame Exactly
        # ----------------------------------------------------
        top_eq = MathTex(
            r"\vec{a} \cdot \vec{b} = a b \cos\theta = a_x b_x + a_y b_y + a_z b_z",
            color=WHITE,
        ).scale(0.85).move_to(LEFT * 3.2 + UP * 2.2)

        diag_offset = RIGHT * 2.5 + UP * 1.5
        vec_b = Arrow(ORIGIN, RIGHT * 3.5, color=PURPLE_COLOR, buff=0).shift(diag_offset)
        vec_a = Arrow(ORIGIN, RIGHT * 2.2 + UP * 1.3, color=PINK_COLOR, buff=0).shift(diag_offset)
        proj_point = diag_offset + RIGHT * 2.2
        proj_line = DashedLine(vec_a.get_end(), proj_point, color=GRAY)

        shadow_glow = create_hazy_line(
            start_pt=diag_offset,
            end_pt=proj_point,
            color=PINK_COLOR,
            core_width=0.05,
            glow_radius=0.40,
            num_layers=30,
            opacity=1.0,
        )

        angle = Angle(vec_b, vec_a, radius=0.7, color=BLUE_COLOR)
        angle_label = (
            MathTex(r"\theta", color=BLUE_COLOR)
            .scale(0.8)
            .next_to(angle, RIGHT, buff=0.1)
            .shift(UP * 0.1)
        )

        label_b = (
            MathTex(r"\vec{b}", color=PURPLE_COLOR)
            .scale(0.9)
            .next_to(vec_b.get_end(), DOWN * 0.4 + RIGHT * 0.1)
        )
        label_a = (
            MathTex(r"\vec{a}", color=PINK_COLOR)
            .scale(0.9)
            .next_to(vec_a.get_end(), UP * 0.2)
        )

        diagram_elements = VGroup(
            top_eq,
            shadow_glow,
            vec_b,
            vec_a,
            proj_line,
            angle,
            angle_label,
            label_b,
            label_a,
        )

        # Match eq1 from Scene 2 end state exactly
        expr_with_dots = MathTex(
            r"\vec{a}", r"\cdot", r"(", r"\vec{b}", r"+", r"\vec{c}", r")"
        ).move_to(UP * 0.25)
        expr_with_dots[4].become(
            MathTex(r"\cdot", color=WHITE).move_to(expr_with_dots[4].get_center())
        )

        equals_sign = MathTex(r"=", color=WHITE).next_to(expr_with_dots, RIGHT, buff=0.25)
        question_marks = MathTex(r"?", r"?", r"?", color=BRIGHT_YELLOW).next_to(
            equals_sign, RIGHT, buff=0.2
        )

        bc_group = VGroup(expr_with_dots[3], expr_with_dots[4], expr_with_dots[5])
        brace_bc = Brace(bc_group, direction=DOWN, color=RED_COLOR)
        label_scalar = (
            MathTex(r"\text{scalar}", color=RED_COLOR)
            .scale(0.85)
            .next_to(brace_bc, DOWN, buff=0.15)
        )

        brace_a = Brace(expr_with_dots[0], direction=DOWN, color=GREEN_COLOR)
        label_vector = (
            MathTex(r"\text{vector}", color=GREEN_COLOR)
            .scale(0.85)
            .next_to(brace_a, DOWN, buff=0.15)
        )

        self.add(
            diagram_elements,
            expr_with_dots,
            equals_sign,
            question_marks,
            brace_bc,
            label_scalar,
            brace_a,
            label_vector,
        )

        # ----------------------------------------------------
        # Timeline Alignment (Start: 34:12 -> t = 0.00s)
        # ----------------------------------------------------
        self.wait(2.00)

        # t = 2.00s (36:12 on timeline)
        self.play(
            FadeOut(diagram_elements),
            FadeOut(question_marks),
            FadeOut(brace_bc),
            FadeOut(label_scalar),
            FadeOut(brace_a),
            FadeOut(label_vector),
            run_time=0.6,
        )

        expr_no_dots = MathTex(r"\vec{a}", r"(", r"\vec{b}", r"\vec{c}", r")").move_to(
            expr_with_dots.get_center()
        )

        self.play(
            expr_with_dots[1].animate.set_color(BRIGHT_YELLOW).scale(1.5),
            expr_with_dots[4].animate.set_color(BRIGHT_YELLOW).scale(1.5),
            run_time=0.4,
        )
        self.play(
            FadeOut(expr_with_dots[1]),
            FadeOut(expr_with_dots[4]),
            TransformMatchingShapes(
                VGroup(
                    expr_with_dots[0],
                    expr_with_dots[2],
                    expr_with_dots[3],
                    expr_with_dots[5],
                    expr_with_dots[6],
                ),
                expr_no_dots,
            ),
            equals_sign.animate.next_to(expr_no_dots, RIGHT, buff=0.25),
            run_time=0.8,
        )

        self.wait(2.87)

        # t = 6.67s (41:04 on timeline)
        rhs_expr = MathTex(r"(", r"\vec{a}", r"\vec{b}", r")", r"\vec{c}").next_to(
            equals_sign, RIGHT, buff=0.25
        )
        self.play(Write(rhs_expr), run_time=0.6)

        self.wait(3.36)

        # t = 10.63s (45:03 on timeline): Move equation UR, fade in image
        full_equation = VGroup(expr_no_dots, equals_sign, rhs_expr)
        img_path = r"C:\Users\ambri\Downloads\A Little Fizzy\Ep1 Dot Product to Geo\Scenes\LinguaMathematica.png"
        inserted_image = ImageMobject(img_path).scale(0.85).to_edge(UP, buff=0.4)

        self.play(
            full_equation.animate.scale(0.8).to_corner(UR, buff=0.8),
            FadeIn(inserted_image),
            run_time=1.0,
        )

        self.wait(7.58)

        # ----------------------------------------------------
        # t = 19.21s (53:17 on timeline): Source chains a, b, c appear below image
        # ----------------------------------------------------
        len_a, len_b, len_c = 0.9, 1.2, 1.5

        chain_a = create_chain_bar(len_a, PINK_COLOR)
        chain_b = create_chain_bar(len_b, PURPLE_COLOR)
        chain_c = create_chain_bar(len_c, BLUE_COLOR)

        lbl_a = MathTex(r"\vec{a}", color=PINK_COLOR).scale(0.8)
        lbl_b = MathTex(r"\vec{b}", color=PURPLE_COLOR).scale(0.8)
        lbl_c = MathTex(r"\vec{c}", color=BLUE_COLOR).scale(0.8)

        item_a = VGroup(lbl_a, chain_a)
        lbl_a.next_to(chain_a, UP, buff=0.12)

        item_b = VGroup(lbl_b, chain_b)
        lbl_b.next_to(chain_b, UP, buff=0.12)

        item_c = VGroup(lbl_c, chain_c)
        lbl_c.next_to(chain_c, UP, buff=0.12)

        source_chains = VGroup(item_a, item_b, item_c).arrange(RIGHT, buff=0.8)
        source_chains.next_to(inserted_image, DOWN, buff=0.4)

        self.play(FadeIn(source_chains), run_time=0.8)

        self.wait(3.95)

        # ----------------------------------------------------
        # t = 23.96s (58:11 on timeline): Construct a(bc) on the left
        # ----------------------------------------------------
        dup_b1 = chain_b.copy()
        dup_c1 = chain_c.copy()

        dup_b1.move_to(LEFT * 2.5 + DOWN * 1.8)
        dup_c1.next_to(dup_b1, RIGHT, buff=0.0)

        self.play(
            TransformFromCopy(chain_b, dup_b1),
            TransformFromCopy(chain_c, dup_c1),
            run_time=0.6,
        )

        dup_a1 = chain_a.copy()
        self.play(
            dup_a1.animate.next_to(dup_b1, LEFT, buff=0.0),
            run_time=0.5,
        )

        self.wait(0.15)

        # ----------------------------------------------------
        # t = 25.21s (59:17 on timeline): Construct (ab)c on the right
        # ----------------------------------------------------
        dup_a2 = chain_a.copy()
        dup_b2 = chain_b.copy()

        dup_a2.move_to(RIGHT * 0.85 + DOWN * 1.8)
        dup_b2.next_to(dup_a2, RIGHT, buff=0.0)

        self.play(
            TransformFromCopy(chain_a, dup_a2),
            TransformFromCopy(chain_b, dup_b2),
            run_time=0.6,
        )

        dup_c2 = chain_c.copy()
        self.play(
            dup_c2.animate.next_to(dup_b2, RIGHT, buff=0.0),
            run_time=0.5,
        )

        self.wait(10.00)
        
        
class Scene4(Scene):
    def construct(self):
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"

        # ----------------------------------------------------
        # Recreate Scene 3 Final Frame Exactly
        # ----------------------------------------------------
        expr_no_dots = MathTex(r"\vec{a}", r"(", r"\vec{b}", r"\vec{c}", r")")
        equals_sign = MathTex(r"=", color=WHITE)
        rhs_expr = MathTex(r"(", r"\vec{a}", r"\vec{b}", r")", r"\vec{c}")

        equals_sign.next_to(expr_no_dots, RIGHT, buff=0.25)
        rhs_expr.next_to(equals_sign, RIGHT, buff=0.25)

        full_equation = VGroup(expr_no_dots, equals_sign, rhs_expr)
        full_equation.scale(0.8).to_corner(UR, buff=0.8)

        img_path = r"C:\Users\ambri\Downloads\A Little Fizzy\Ep1 Dot Product to Geo\Scenes\LinguaMathematica.png"
        inserted_image = ImageMobject(img_path).scale(0.85).to_edge(UP, buff=0.4)

        len_a, len_b, len_c = 0.9, 1.2, 1.5

        def create_chain_bar(length, color, height=0.25):
            rect = RoundedRectangle(
                corner_radius=0.1, height=height, width=length, color=color, fill_opacity=0.25
            )
            num_links = max(2, int(length / 0.35))
            links = VGroup()
            for i in range(num_links):
                link_w = length / num_links
                link = RoundedRectangle(
                    corner_radius=0.06, height=height * 0.75, width=link_w, color=color
                )
                link.move_to(rect.get_left() + RIGHT * (i + 0.5) * link_w)
                links.add(link)
            return VGroup(rect, links)

        chain_a = create_chain_bar(len_a, PINK_COLOR)
        chain_b = create_chain_bar(len_b, PURPLE_COLOR)
        chain_c = create_chain_bar(len_c, BLUE_COLOR)

        lbl_a = MathTex(r"\vec{a}", color=PINK_COLOR).scale(0.8)
        lbl_b = MathTex(r"\vec{b}", color=PURPLE_COLOR).scale(0.8)
        lbl_c = MathTex(r"\vec{c}", color=BLUE_COLOR).scale(0.8)

        item_a = VGroup(lbl_a, chain_a)
        lbl_a.next_to(chain_a, UP, buff=0.12)

        item_b = VGroup(lbl_b, chain_b)
        lbl_b.next_to(chain_b, UP, buff=0.12)

        item_c = VGroup(lbl_c, chain_c)
        lbl_c.next_to(chain_c, UP, buff=0.12)

        source_chains = VGroup(item_a, item_b, item_c).arrange(RIGHT, buff=0.8)
        source_chains.next_to(inserted_image, DOWN, buff=0.4)

        dup_b1 = chain_b.copy().move_to(LEFT * 2.5 + DOWN * 1.8)
        dup_c1 = chain_c.copy().next_to(dup_b1, RIGHT, buff=0.0)
        dup_a1 = chain_a.copy().next_to(dup_b1, LEFT, buff=0.0)

        dup_a2 = chain_a.copy().move_to(RIGHT * 0.85 + DOWN * 1.8)
        dup_b2 = chain_b.copy().next_to(dup_a2, RIGHT, buff=0.0)
        dup_c2 = chain_c.copy().next_to(dup_b2, RIGHT, buff=0.0)

        self.add(
            full_equation,
            inserted_image,
            source_chains,
            dup_b1,
            dup_c1,
            dup_a1,
            dup_a2,
            dup_b2,
            dup_c2,
        )

        # ----------------------------------------------------
        # Timeline Alignment (Start: 1:06:12 -> t = 0.00s)
        # ----------------------------------------------------
        self.wait(1.00)

        # t = 1.00s (1:07:12 on timeline)
        other_elements = Group(
            equals_sign,
            rhs_expr,
            inserted_image,
            source_chains,
            dup_b1,
            dup_c1,
            dup_a1,
            dup_a2,
            dup_b2,
            dup_c2,
        )

        self.play(
            expr_no_dots.animate.scale(1.25).move_to(UP * 2.2),
            FadeOut(other_elements),
            run_time=1.8,
        )

        self.wait(7.58)

        # ----------------------------------------------------
        # t = 10.38s (1:16:21 on timeline): Symmetric Line
        # ----------------------------------------------------
        sym_line = MathTex(
            r"\text{Symmetric} \quad", r"\vec{b}", r"\vec{a}", r"=", r"\vec{a}", r"\vec{b}",
            arg_separator=""
        ).scale(0.9)
        sym_line.next_to(expr_no_dots, DOWN, buff=0.8).to_edge(LEFT, buff=1.2)

        self.play(Write(sym_line[0]), run_time=0.8)
        self.play(FadeIn(VGroup(sym_line[1], sym_line[2])), run_time=0.8)

        b_copy = sym_line[1].copy()
        a_copy = sym_line[2].copy()

        sym_eq = sym_line[3]
        sym_eq.set_opacity(0)
        self.add(sym_eq)

        self.play(
            b_copy.animate.move_to(sym_line[5]),
            a_copy.animate.move_to(sym_line[4]),
            sym_eq.animate.set_opacity(1),
            run_time=1.2,
        )
        self.add(sym_line[4], sym_line[5])
        self.remove(b_copy, a_copy)

        self.wait(0.24)

        # ----------------------------------------------------
        # t = 13.42s (1:19:22 on timeline): Antisymmetric Line
        # ----------------------------------------------------
        antisym_line = MathTex(
            r"\text{Antisymmetric} \quad", r"\vec{b}", r"\vec{a}", r"=", r"-", r"\vec{a}", r"\vec{b}",
            arg_separator=""
        ).scale(0.9)
        antisym_line.next_to(sym_line, DOWN, buff=0.6).align_to(sym_line[0], LEFT)

        self.play(Write(antisym_line[0]), run_time=0.8)
        self.play(FadeIn(VGroup(antisym_line[1], antisym_line[2])), run_time=0.8)

        anti_b_copy = antisym_line[1].copy()
        anti_a_copy = antisym_line[2].copy()

        anti_eq = antisym_line[3]
        anti_minus = antisym_line[4]
        anti_eq.set_opacity(0)
        anti_minus.set_opacity(0)
        self.add(anti_eq, anti_minus)

        self.play(
            anti_b_copy.animate.move_to(antisym_line[6]),
            anti_a_copy.animate.move_to(antisym_line[5]),
            anti_eq.animate.set_opacity(1),
            anti_minus.animate.set_opacity(1),
            run_time=1.2,
        )
        self.add(antisym_line[5], antisym_line[6])
        self.remove(anti_b_copy, anti_a_copy)

        self.wait(4.82)

        # ----------------------------------------------------
        # t = 21.04s (1:27:13 on timeline): Move a(bc) -> ab left
        # ----------------------------------------------------
        ab_lhs = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1).move_to(LEFT * 5.0 + UP * 2.2)

        self.play(
            ReplacementTransform(expr_no_dots, ab_lhs),
            FadeOut(sym_line),
            FadeOut(antisym_line),
            run_time=1.8,
        )

        self.wait(0.49)

        # ----------------------------------------------------
        # t = 23.33s (1:29:20 on timeline): Discrete fraction assembly
        # ----------------------------------------------------
        eq_sign_2 = MathTex("=").scale(1.1).next_to(ab_lhs, RIGHT, buff=0.35)

        ab1 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab1 = MathTex("2").scale(1.1)
        bar_ab1 = Line(ORIGIN, RIGHT * (ab1.width + 0.2), stroke_width=2)
        ab1.next_to(bar_ab1, UP, buff=0.15)
        den_ab1.next_to(bar_ab1, DOWN, buff=0.15)
        frac1 = VGroup(ab1, bar_ab1, den_ab1).next_to(eq_sign_2, RIGHT, buff=0.35)

        plus_mid = MathTex("+").scale(1.1).next_to(frac1, RIGHT, buff=0.35)

        ab2 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab2 = MathTex("2").scale(1.1)
        bar_ab2 = Line(ORIGIN, RIGHT * (ab2.width + 0.2), stroke_width=2)
        ab2.next_to(bar_ab2, UP, buff=0.15)
        den_ab2.next_to(bar_ab2, DOWN, buff=0.15)
        frac2 = VGroup(ab2, bar_ab2, den_ab2).next_to(plus_mid, RIGHT, buff=0.35)

        self.play(FadeIn(eq_sign_2), run_time=0.5)
        self.play(
            TransformFromCopy(ab_lhs, ab1),
            FadeIn(bar_ab1),
            FadeIn(den_ab1),
            FadeIn(plus_mid),
            TransformFromCopy(ab_lhs, ab2),
            FadeIn(bar_ab2),
            FadeIn(den_ab2),
            run_time=1.4,
        )

        self.wait(6.67)

        # ----------------------------------------------------
        # t = 31.90s (1:38:05 on timeline): Append + 0
        # ----------------------------------------------------
        plus0 = MathTex("+").scale(1.1).next_to(frac2, RIGHT, buff=0.4)
        zero = MathTex("0").scale(1.1).next_to(plus0, RIGHT, buff=0.4)

        self.play(FadeIn(plus0), FadeIn(zero), run_time=0.8)

        self.wait(2.20)

        # ----------------------------------------------------
        # t = 34.90s (1:41:05 on timeline): 0 becomes ba/2 - ba/2
        # ----------------------------------------------------
        ba1 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)
        den_ba1 = MathTex("2").scale(1.1)
        bar_ba1 = Line(ORIGIN, RIGHT * (ba1.width + 0.2), stroke_width=2)
        ba1.next_to(bar_ba1, UP, buff=0.15)
        den_ba1.next_to(bar_ba1, DOWN, buff=0.15)
        frac3 = VGroup(ba1, bar_ba1, den_ba1)

        minus_ba = MathTex("-").scale(1.1)

        ba2 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)
        den_ba2 = MathTex("2").scale(1.1)
        bar_ba2 = Line(ORIGIN, RIGHT * (ba2.width + 0.2), stroke_width=2)
        ba2.next_to(bar_ba2, UP, buff=0.15)
        den_ba2.next_to(bar_ba2, DOWN, buff=0.15)
        frac4 = VGroup(ba2, bar_ba2, den_ba2)

        ba_expansion = VGroup(frac3, minus_ba, frac4).arrange(RIGHT, buff=0.35)
        ba_expansion.next_to(plus0, RIGHT, buff=0.35)

        self.play(
            ReplacementTransform(zero, ba_expansion),
            run_time=1.0,
        )

        self.wait(1.00)

        # ----------------------------------------------------
        # t = 36.90s (1:43:09 on timeline): Left Rigid Combination
        # ----------------------------------------------------
        dum_num_L = VGroup(ab1.copy(), plus0.copy(), ba1.copy()).arrange(RIGHT, buff=0.25)
        dum_num_L.shift(ab1.get_center() - dum_num_L[0].get_center())

        t_ab1 = ab1.copy().move_to(dum_num_L[0])
        t_plus0 = plus0.copy().move_to(dum_num_L[1])
        t_ba1 = ba1.copy().move_to(dum_num_L[2])

        t_bar_L = Line(dum_num_L.get_left() + LEFT * 0.1, dum_num_L.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_L.set_y(bar_ab1.get_y())
        t_den_L = den_ab1.copy().set_x(t_bar_L.get_x())

        shift_amount = t_bar_L.get_right()[0] - bar_ab1.get_right()[0]

        self.play(
            ab1.animate.move_to(t_ab1),
            plus0.animate.move_to(t_plus0),
            ba1.animate.move_to(t_ba1),
            bar_ab1.animate.put_start_and_end_on(t_bar_L.get_start(), t_bar_L.get_end()),
            bar_ba1.animate.put_start_and_end_on(t_bar_L.get_start(), t_bar_L.get_end()),
            den_ab1.animate.move_to(t_den_L),
            den_ba1.animate.move_to(t_den_L),
            plus_mid.animate.shift(RIGHT * shift_amount),
            ab2.animate.shift(RIGHT * shift_amount),
            bar_ab2.animate.shift(RIGHT * shift_amount),
            den_ab2.animate.shift(RIGHT * shift_amount),
            minus_ba.animate.shift(RIGHT * shift_amount),
            ba2.animate.shift(RIGHT * shift_amount),
            bar_ba2.animate.shift(RIGHT * shift_amount),
            den_ba2.animate.shift(RIGHT * shift_amount),
            run_time=1.0,
        )
        self.remove(bar_ba1, den_ba1)

        self.wait(0.30)

        # ----------------------------------------------------
        # t = 38.20s: Right Rigid Combination
        # ----------------------------------------------------
        dum_num_R = VGroup(ab2.copy(), minus_ba.copy(), ba2.copy()).arrange(RIGHT, buff=0.25)
        dum_num_R.shift(ab2.get_center() - dum_num_R[0].get_center())

        t_ab2 = ab2.copy().move_to(dum_num_R[0])
        t_minus = minus_ba.copy().move_to(dum_num_R[1])
        t_ba2 = ba2.copy().move_to(dum_num_R[2])

        t_bar_R = Line(dum_num_R.get_left() + LEFT * 0.1, dum_num_R.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_R.set_y(bar_ab2.get_y())
        t_den_R = den_ab2.copy().set_x(t_bar_R.get_x())

        self.play(
            ab2.animate.move_to(t_ab2),
            minus_ba.animate.move_to(t_minus),
            ba2.animate.move_to(t_ba2),
            bar_ab2.animate.put_start_and_end_on(t_bar_R.get_start(), t_bar_R.get_end()),
            bar_ba2.animate.put_start_and_end_on(t_bar_R.get_start(), t_bar_R.get_end()),
            den_ab2.animate.move_to(t_den_R),
            den_ba2.animate.move_to(t_den_R),
            run_time=1.0,
        )
        self.remove(bar_ba2, den_ba2)

        # ----------------------------------------------------
        # t = 39.20s (1:45:18 on timeline): Rigid horizontal glyph swaps
        # ----------------------------------------------------
        pos_x_a_ab1 = ab1[0].get_x()
        pos_x_b_ab1 = ab1[1].get_x()
        pos_x_b_ba1 = ba1[0].get_x()
        pos_x_a_ba1 = ba1[1].get_x()

        self.play(
            ab1[0].animate.set_x(pos_x_b_ab1),
            ab1[1].animate.set_x(pos_x_a_ab1),
            ba1[0].animate.set_x(pos_x_a_ba1),
            ba1[1].animate.set_x(pos_x_b_ba1),
            run_time=0.8
        )
        
        self.wait(0.50)
        
        self.play(
            ab1[0].animate.set_x(pos_x_a_ab1),
            ab1[1].animate.set_x(pos_x_b_ab1),
            ba1[0].animate.set_x(pos_x_b_ba1),
            ba1[1].animate.set_x(pos_x_a_ba1),
            run_time=0.8
        )

        self.wait(0.16)

        # ----------------------------------------------------
        # t = 41.46s (1:47:23 on timeline)
        # ----------------------------------------------------
        pos_x_a_ab2 = ab2[0].get_x()
        pos_x_b_ab2 = ab2[1].get_x()
        pos_x_b_ba2 = ba2[0].get_x()
        pos_x_a_ba2 = ba2[1].get_x()

        self.play(
            ab2[0].animate.set_x(pos_x_b_ab2),
            ab2[1].animate.set_x(pos_x_a_ab2),
            ba2[0].animate.set_x(pos_x_a_ba2),
            ba2[1].animate.set_x(pos_x_b_ba2),
            run_time=0.8
        )
        
        self.wait(0.50)
        
        self.play(
            ab2[0].animate.set_x(pos_x_a_ab2),
            ab2[1].animate.set_x(pos_x_b_ab2),
            ba2[0].animate.set_x(pos_x_b_ba2),
            ba2[1].animate.set_x(pos_x_a_ba2),
            run_time=0.8
        )

        # Tail buffer for timeline expansion
        self.wait(10.00)
        
        
class Scene5(Scene):
    def construct(self):
        # ----------------------------------------------------
        # Recreate Scene 4 Final Frame Exactly
        # By mirroring the exact construction steps of Scene 4, 
        # we guarantee a pixel-perfect start for Scene 5.
        # ----------------------------------------------------
        ab_lhs = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1).move_to(LEFT * 5.0 + UP * 2.2)
        eq_sign_2 = MathTex("=").scale(1.1).next_to(ab_lhs, RIGHT, buff=0.35)

        # Base components for the left fraction
        ab1 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab1 = MathTex("2").scale(1.1)
        bar_ab1 = Line(ORIGIN, RIGHT * (ab1.width + 0.2), stroke_width=2)
        ab1.next_to(bar_ab1, UP, buff=0.15)
        den_ab1.next_to(bar_ab1, DOWN, buff=0.15)
        frac1_dummy = VGroup(ab1, bar_ab1, den_ab1).next_to(eq_sign_2, RIGHT, buff=0.35)

        plus_mid = MathTex("+").scale(1.1).next_to(frac1_dummy, RIGHT, buff=0.35)

        # Base components for the right fraction
        ab2 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab2 = MathTex("2").scale(1.1)
        bar_ab2 = Line(ORIGIN, RIGHT * (ab2.width + 0.2), stroke_width=2)
        ab2.next_to(bar_ab2, UP, buff=0.15)
        den_ab2.next_to(bar_ab2, DOWN, buff=0.15)
        frac2_dummy = VGroup(ab2, bar_ab2, den_ab2).next_to(plus_mid, RIGHT, buff=0.35)

        plus0 = MathTex("+").scale(1.1).next_to(frac2_dummy, RIGHT, buff=0.4)
        ba1 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)
        
        minus_ba = MathTex("-").scale(1.1)
        ba2 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)

        # Build the final left fraction state
        dum_num_L = VGroup(ab1.copy(), plus0.copy(), ba1.copy()).arrange(RIGHT, buff=0.25)
        dum_num_L.shift(ab1.get_center() - dum_num_L[0].get_center())

        ab1.move_to(dum_num_L[0])
        plus0.move_to(dum_num_L[1])
        ba1.move_to(dum_num_L[2])

        t_bar_L = Line(dum_num_L.get_left() + LEFT * 0.1, dum_num_L.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_L.set_y(bar_ab1.get_y())
        t_den_L = den_ab1.copy().set_x(t_bar_L.get_x())

        # Shift the middle plus and right elements just like Scene 4
        shift_amount = t_bar_L.get_right()[0] - bar_ab1.get_right()[0]
        plus_mid.shift(RIGHT * shift_amount)
        ab2.shift(RIGHT * shift_amount)
        bar_ab2.shift(RIGHT * shift_amount)
        den_ab2.shift(RIGHT * shift_amount)

        # Build the final right fraction state
        dum_num_R = VGroup(ab2.copy(), minus_ba.copy(), ba2.copy()).arrange(RIGHT, buff=0.25)
        dum_num_R.shift(ab2.get_center() - dum_num_R[0].get_center())

        ab2.move_to(dum_num_R[0])
        minus_ba.move_to(dum_num_R[1])
        ba2.move_to(dum_num_R[2])

        t_bar_R = Line(dum_num_R.get_left() + LEFT * 0.1, dum_num_R.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_R.set_y(bar_ab2.get_y())
        t_den_R = den_ab2.copy().set_x(t_bar_R.get_x())

        # Add all elements to the scene
        self.add(
            ab_lhs, eq_sign_2, 
            ab1, plus0, ba1, t_bar_L, t_den_L, 
            plus_mid, 
            ab2, minus_ba, ba2, t_bar_R, t_den_R
        )

        # Create groups for easy referencing during the rising animations
        frac_L = VGroup(ab1, plus0, ba1, t_bar_L, t_den_L)
        frac_R = VGroup(ab2, minus_ba, ba2, t_bar_R, t_den_R)

        # ----------------------------------------------------
        # Timeline Alignment (Start: 1:52:23 -> t = 0.00s)
        # ----------------------------------------------------
        self.wait(0.50)

        # ----------------------------------------------------
        # t = 0.50s (approx 1:52:15): "a dot b = b dot a" appears
        # ----------------------------------------------------
        dot_eq = MathTex(r"\vec{a} \cdot \vec{b}", r"=", r"\vec{b} \cdot \vec{a}").scale(1.1)
        
        dot_eq.next_to(frac_L, DOWN, buff=1.5)

        # Align "a dot b" perfectly under the left fraction
        x_offset = frac_L.get_x() - dot_eq[0].get_x()
        dot_eq.shift(RIGHT * x_offset)

        self.play(FadeIn(dot_eq), run_time=0.8)

        # Hold until 2:00:08 (7.38s relative to 1:52:23 start)
        self.wait(6.08)

        # ----------------------------------------------------
        # t = 7.38s (2:00:08 on timeline): Rigid vertical rise and cross-fade
        # ----------------------------------------------------
        self.play(
            dot_eq[0].animate.set_y(frac_L.get_y()),
            FadeOut(frac_L),
            FadeOut(dot_eq[1]),
            FadeOut(dot_eq[2]),
            run_time=1.2
        )

        # ----------------------------------------------------
        # t = 11.29s (2:04:06 on timeline): "a wedge b \triangleq - b wedge a" appears
        # ----------------------------------------------------
        self.wait(2.71)

        wedge_eq = MathTex(r"\vec{a} \wedge \vec{b}", r"\triangleq", r"- \vec{b} \wedge \vec{a}").scale(1.1)
        wedge_eq.next_to(frac_R, DOWN, buff=1.5)

        # Align "a wedge b" perfectly under the right fraction
        x_offset_wedge = frac_R.get_x() - wedge_eq[0].get_x()
        wedge_eq.shift(RIGHT * x_offset_wedge)

        footnote = Tex(
            r"*\textit{$\triangleq$ is used to mean ``this new notation is such that both expressions are equal''}",
            color=LIGHT_GREY
        ).scale(0.65).to_edge(DOWN, buff=0.5)

        self.play(
            FadeIn(wedge_eq),
            FadeIn(footnote),
            run_time=0.8
        )

        # ----------------------------------------------------
        # t = 13.71s (2:06:16 on timeline): Rigid vertical rise and cross-fade
        # ----------------------------------------------------
        self.wait(1.62)

        self.play(
            wedge_eq[0].animate.set_y(frac_R.get_y()),
            FadeOut(frac_R),
            FadeOut(wedge_eq[1]),
            FadeOut(wedge_eq[2]),
            FadeOut(footnote),
            run_time=1.2
        )

        # Tail buffer for timeline expansion
        self.wait(10.00)
        
        
class Scene6(Scene):
    def construct(self):
        # ----------------------------------------------------
        # Recreate Scene 5 Final Frame Exactly
        # Dummy fractions are constructed to determine the exact
        # anchor coordinates that the dot and wedge terms snap to.
        # ----------------------------------------------------
        ab_lhs = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1).move_to(LEFT * 5.0 + UP * 2.2)
        eq_sign_2 = MathTex("=").scale(1.1).next_to(ab_lhs, RIGHT, buff=0.35)

        # Base components for the left fraction from previous construction
        ab1 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab1 = MathTex("2").scale(1.1)
        bar_ab1 = Line(ORIGIN, RIGHT * (ab1.width + 0.2), stroke_width=2)
        ab1.next_to(bar_ab1, UP, buff=0.15)
        den_ab1.next_to(bar_ab1, DOWN, buff=0.15)
        frac1_dummy = VGroup(ab1, bar_ab1, den_ab1).next_to(eq_sign_2, RIGHT, buff=0.35)

        plus_mid = MathTex("+").scale(1.1).next_to(frac1_dummy, RIGHT, buff=0.35)

        # Base components for the right fraction from previous construction
        ab2 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab2 = MathTex("2").scale(1.1)
        bar_ab2 = Line(ORIGIN, RIGHT * (ab2.width + 0.2), stroke_width=2)
        ab2.next_to(bar_ab2, UP, buff=0.15)
        den_ab2.next_to(bar_ab2, DOWN, buff=0.15)
        frac2_dummy = VGroup(ab2, bar_ab2, den_ab2).next_to(plus_mid, RIGHT, buff=0.35)

        plus0 = MathTex("+").scale(1.1).next_to(frac2_dummy, RIGHT, buff=0.4)
        ba1 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)
        
        minus_ba = MathTex("-").scale(1.1)
        ba2 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)

        # Build the expanded left fraction width to find the correct center
        dum_num_L = VGroup(ab1.copy(), plus0.copy(), ba1.copy()).arrange(RIGHT, buff=0.25)
        dum_num_L.shift(ab1.get_center() - dum_num_L[0].get_center())

        t_bar_L = Line(dum_num_L.get_left() + LEFT * 0.1, dum_num_L.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_L.set_y(bar_ab1.get_y())
        t_den_L = den_ab1.copy().set_x(t_bar_L.get_x())

        # Shift the middle plus and right elements according to the expanded fraction
        shift_amount = t_bar_L.get_right()[0] - bar_ab1.get_right()[0]
        plus_mid.shift(RIGHT * shift_amount)
        frac2_dummy.shift(RIGHT * shift_amount)

        # Build the expanded right fraction width to find the correct center
        dum_num_R = VGroup(ab2.copy(), minus_ba.copy(), ba2.copy()).arrange(RIGHT, buff=0.25)
        dum_num_R.shift(ab2.get_center() - dum_num_R[0].get_center())

        t_bar_R = Line(dum_num_R.get_left() + LEFT * 0.1, dum_num_R.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_R.set_y(bar_ab2.get_y())
        t_den_R = den_ab2.copy().set_x(t_bar_R.get_x())

        # Recreate the exact structural VGroups from Scene 5's crossfade
        ab1.move_to(dum_num_L[0])
        plus0.move_to(dum_num_L[1])
        ba1.move_to(dum_num_L[2])
        frac_L = VGroup(ab1, plus0, ba1, t_bar_L, t_den_L)

        ab2.move_to(dum_num_R[0])
        minus_ba.move_to(dum_num_R[1])
        ba2.move_to(dum_num_R[2])
        frac_R = VGroup(ab2, minus_ba, ba2, t_bar_R, t_den_R)

        # Final positioned terms for Scene 5's ending aligned to the fractions
        dot_term = MathTex(r"\vec{a} \cdot \vec{b}").scale(1.1).move_to(frac_L)
        wedge_term = MathTex(r"\vec{a} \wedge \vec{b}").scale(1.1).move_to(frac_R)

        # Add the inherited elements to the scene
        self.add(ab_lhs, eq_sign_2, dot_term, plus_mid, wedge_term)

        # ----------------------------------------------------
        # Timeline Alignment (Start: 2:10:12 -> t = 0.00s)
        # ----------------------------------------------------
        # Wait until 2:11:10 (t = 0.98s)
        self.wait(0.98)

        # ----------------------------------------------------
        # t = 0.98s (2:11:10 on timeline): Write a^2
        # Align perfectly on the x-axis with the terms directly above
        # ----------------------------------------------------
        y_offset = 1.5

        a_sq = MathTex(r"\vec{a}^2").scale(1.1)
        a_sq.set_x(ab_lhs.get_x())
        a_sq.set_y(ab_lhs.get_y() - y_offset)

        self.play(Write(a_sq), run_time=0.8)

        # Wait until 2:12:22 (t = 2.10s)
        # (0.98s + 0.8s animation = 1.78s. 2.10s - 1.78s = 0.32s)
        self.wait(0.32)

        # ----------------------------------------------------
        # t = 2.10s (2:12:22 on timeline): Append = a dot a + a wedge a
        # ----------------------------------------------------
        a_sq_eq = MathTex("=").scale(1.1)
        a_sq_eq.set_x(eq_sign_2.get_x())
        a_sq_eq.set_y(eq_sign_2.get_y() - y_offset)

        dot_aa = MathTex(r"\vec{a} \cdot \vec{a}").scale(1.1)
        dot_aa.set_x(dot_term.get_x())
        dot_aa.set_y(dot_term.get_y() - y_offset)

        plus_aa = MathTex("+").scale(1.1)
        plus_aa.set_x(plus_mid.get_x())
        plus_aa.set_y(plus_mid.get_y() - y_offset)

        wedge_aa = MathTex(r"\vec{a} \wedge \vec{a}").scale(1.1)
        wedge_aa.set_x(wedge_term.get_x())
        wedge_aa.set_y(wedge_term.get_y() - y_offset)

        self.play(
            Write(a_sq_eq),
            Write(dot_aa),
            Write(plus_aa),
            Write(wedge_aa),
            run_time=1.0
        )

        # Wait until 2:15:02 (t = 4.90s)
        # (2.10s + 1.0s animation = 3.10s. 4.90s - 3.10s = 1.80s)
        self.wait(1.80)

        # ----------------------------------------------------
        # t = 4.90s (2:15:02 on timeline): Strike through and text
        # ----------------------------------------------------
        DARK_RED_COLOR = "#8B0000"

        strike = Arrow(
            start=wedge_aa.get_corner(DL) + LEFT * 0.15 + DOWN * 0.15,
            end=wedge_aa.get_corner(UR) + RIGHT * 0.15 + UP * 0.15,
            color=DARK_RED_COLOR,
            stroke_width=4,
            tip_length=0.15, 
            buff=0
        )
        
        zero_lbl = MathTex("0", color=DARK_RED_COLOR).scale(0.95)
        zero_lbl.next_to(strike.get_end(), RIGHT, buff=0.1).shift(UP * 0.1)

        aa_eq_0 = MathTex(r"\frac{\vec{a}\vec{a} - \vec{a}\vec{a}}{2} = 0", color="#C0C000").scale(0.95)
        aa_eq_0.next_to(wedge_aa, DOWN, buff=0.7)

        self.play(
            GrowArrow(strike),
            FadeIn(zero_lbl),
            FadeIn(aa_eq_0),
            run_time=1.0
        )

        # Wait until 2:17:12 (t = 7.00s)
        # (4.90s + 1.0s animation = 5.90s. 7.00s - 5.90s = 1.10s)
        self.wait(1.10)

        # ----------------------------------------------------
        # t = 7.00s (2:17:12 on timeline): Sequential Fade Out and Append
        # ----------------------------------------------------
        self.play(
            FadeOut(plus_aa),
            FadeOut(wedge_aa),
            FadeOut(strike),
            FadeOut(zero_lbl),
            FadeOut(aa_eq_0),
            run_time=0.6
        )

        self.wait(0.50)

        mag_sq_eq = MathTex("=").scale(1.1).next_to(dot_aa, RIGHT, buff=0.35)
        mag_sq = MathTex(r"|\vec{a}|^2").scale(1.1).next_to(mag_sq_eq, RIGHT, buff=0.35)

        self.play(
            FadeIn(mag_sq_eq),
            FadeIn(mag_sq),
            run_time=0.6
        )

        self.wait(0.60)

        tri_eq = MathTex(r"\triangleq").scale(1.1).next_to(mag_sq, RIGHT, buff=0.35)
        a_sq_scalar = MathTex(r"a^2").scale(1.1).next_to(tri_eq, RIGHT, buff=0.35)

        self.play(
            FadeIn(tri_eq),
            FadeIn(a_sq_scalar),
            run_time=0.5
        )

        # Wait until 2:22:14 (t = 12.02s)
        # (7.00s + delays + runtimes = 9.80s. 12.02s - 9.80s = 2.22s)
        self.wait(2.22)

        # ----------------------------------------------------
        # t = 12.02s (2:22:14 on timeline): Collapse the line
        # ----------------------------------------------------
        target_a_sq_scalar = a_sq_scalar.copy().next_to(a_sq_eq, RIGHT, buff=0.35)

        self.play(
            FadeOut(dot_aa),
            FadeOut(mag_sq_eq),
            FadeOut(mag_sq),
            FadeOut(tri_eq),
            a_sq_scalar.animate.move_to(target_a_sq_scalar),
            run_time=1.2
        )

        # Tail buffer for timeline expansion
        self.wait(10.00)
        
        
class Scene7(Scene):
    def construct(self):
        # ----------------------------------------------------
        # Recreate Scene 6 Final Frame Exactly
        # ----------------------------------------------------
        ab_lhs = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1).move_to(LEFT * 5.0 + UP * 2.2)
        eq_sign_2 = MathTex("=").scale(1.1).next_to(ab_lhs, RIGHT, buff=0.35)

        ab1 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab1 = MathTex("2").scale(1.1)
        bar_ab1 = Line(ORIGIN, RIGHT * (ab1.width + 0.2), stroke_width=2)
        ab1.next_to(bar_ab1, UP, buff=0.15)
        den_ab1.next_to(bar_ab1, DOWN, buff=0.15)
        frac1_dummy = VGroup(ab1, bar_ab1, den_ab1).next_to(eq_sign_2, RIGHT, buff=0.35)

        plus_mid = MathTex("+").scale(1.1).next_to(frac1_dummy, RIGHT, buff=0.35)

        ab2 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab2 = MathTex("2").scale(1.1)
        bar_ab2 = Line(ORIGIN, RIGHT * (ab2.width + 0.2), stroke_width=2)
        ab2.next_to(bar_ab2, UP, buff=0.15)
        den_ab2.next_to(bar_ab2, DOWN, buff=0.15)
        frac2_dummy = VGroup(ab2, bar_ab2, den_ab2).next_to(plus_mid, RIGHT, buff=0.35)

        plus0 = MathTex("+").scale(1.1).next_to(frac2_dummy, RIGHT, buff=0.4)
        ba1 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)
        
        minus_ba = MathTex("-").scale(1.1)
        ba2 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)

        dum_num_L = VGroup(ab1.copy(), plus0.copy(), ba1.copy()).arrange(RIGHT, buff=0.25)
        dum_num_L.shift(ab1.get_center() - dum_num_L[0].get_center())

        t_bar_L = Line(dum_num_L.get_left() + LEFT * 0.1, dum_num_L.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_L.set_y(bar_ab1.get_y())
        t_den_L = den_ab1.copy().set_x(t_bar_L.get_x())

        shift_amount = t_bar_L.get_right()[0] - bar_ab1.get_right()[0]
        plus_mid.shift(RIGHT * shift_amount)
        frac2_dummy.shift(RIGHT * shift_amount)

        dum_num_R = VGroup(ab2.copy(), minus_ba.copy(), ba2.copy()).arrange(RIGHT, buff=0.25)
        dum_num_R.shift(ab2.get_center() - dum_num_R[0].get_center())

        t_bar_R = Line(dum_num_R.get_left() + LEFT * 0.1, dum_num_R.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_R.set_y(bar_ab2.get_y())
        t_den_R = den_ab2.copy().set_x(t_bar_R.get_x())

        ab1.move_to(dum_num_L[0])
        plus0.move_to(dum_num_L[1])
        ba1.move_to(dum_num_L[2])
        frac_L = VGroup(ab1, plus0, ba1, t_bar_L, t_den_L)

        ab2.move_to(dum_num_R[0])
        minus_ba.move_to(dum_num_R[1])
        ba2.move_to(dum_num_R[2])
        frac_R = VGroup(ab2, minus_ba, ba2, t_bar_R, t_den_R)

        dot_term = MathTex(r"\vec{a} \cdot \vec{b}").scale(1.1).move_to(frac_L)
        wedge_term = MathTex(r"\vec{a} \wedge \vec{b}").scale(1.1).move_to(frac_R)

        y_offset = 1.5

        a_sq = MathTex(r"\vec{a}^2").scale(1.1)
        a_sq.set_x(ab_lhs.get_x())
        a_sq.set_y(ab_lhs.get_y() - y_offset)

        a_sq_eq = MathTex("=").scale(1.1)
        a_sq_eq.set_x(eq_sign_2.get_x())
        a_sq_eq.set_y(eq_sign_2.get_y() - y_offset)

        a_sq_scalar = MathTex(r"a^2").scale(1.1).next_to(a_sq_eq, RIGHT, buff=0.35)

        self.add(ab_lhs, eq_sign_2, dot_term, plus_mid, wedge_term, a_sq, a_sq_eq, a_sq_scalar)

        # ----------------------------------------------------
        # Timeline Alignment (Start: 2:24:01 -> t = 0.00s)
        # ----------------------------------------------------
        self.wait(2.59)

        # Fade out second line
        self.play(
            FadeOut(a_sq),
            FadeOut(a_sq_eq),
            FadeOut(a_sq_scalar),
            run_time=0.6
        )

        self.wait(0.85)

        # Write and slide abba (Line 2)
        target_abba = MathTex(r"\vec{a}", r"\vec{b}", r"\vec{b}", r"\vec{a}", arg_separator=r"\;").scale(1.1)
        target_abba.align_to(ab_lhs, LEFT)
        target_abba.set_y(ab_lhs.get_y() - y_offset)

        start_ab = VGroup(target_abba[0].copy(), target_abba[1].copy())
        start_ab.shift(LEFT * 1.5)

        start_ba = VGroup(target_abba[2].copy(), target_abba[3].copy())
        start_ba.shift(RIGHT * 1.5)

        self.play(Write(start_ab), run_time=0.4)
        self.play(Write(start_ba), run_time=0.4)
        self.wait(0.40)

        self.play(
            start_ab[0].animate.set_x(target_abba[0].get_x()),
            start_ab[1].animate.set_x(target_abba[1].get_x()),
            start_ba[0].animate.set_x(target_abba[2].get_x()),
            start_ba[1].animate.set_x(target_abba[3].get_x()),
            run_time=0.8
        )

        a1 = start_ab[0]
        b1 = start_ab[1]
        b2 = start_ba[0]
        a2 = start_ba[1]

        self.wait(6.97)

        # Morph b -> b^2
        a_bsq_a = MathTex(r"\vec{a}", r"b^2", r"\vec{a}", arg_separator=r"\;").scale(1.1)
        a_bsq_a.align_to(target_abba, LEFT).set_y(target_abba.get_y())
        
        self.play(
            a1.animate.set_x(a_bsq_a[0].get_x()),
            a2.animate.set_x(a_bsq_a[2].get_x()),
            b1.animate.move_to(a_bsq_a[1].get_center()).set_opacity(0),
            b2.animate.move_to(a_bsq_a[1].get_center()).set_opacity(0),
            FadeIn(a_bsq_a[1]),
            run_time=1.0
        )
        self.remove(b1, b2)
        
        bsq = a_bsq_a[1]

        self.wait(4.20)

        # Slide letters past each other
        aa_bsq = MathTex(r"\vec{a}", r"\vec{a}", r"b^2", arg_separator=r"\;").scale(1.1)
        aa_bsq.align_to(a_bsq_a, LEFT).set_y(a_bsq_a.get_y())

        self.play(
            a1.animate.set_x(aa_bsq[0].get_x()),
            a2.animate.set_x(aa_bsq[1].get_x()),
            bsq.animate.set_x(aa_bsq[2].get_x()),
            run_time=1.0
        )

        self.wait(2.84)

        # Morph a -> a^2 
        # (Creates asq_bsq cleanly as a fully realized parent container to prevent ghosting)
        asq_bsq = MathTex(r"a^2", r"b^2", arg_separator=r"\;").scale(1.1)
        asq_bsq.align_to(aa_bsq, LEFT).set_y(aa_bsq.get_y())

        self.play(
            a1.animate.move_to(asq_bsq[0].get_center()).set_opacity(0),
            a2.animate.move_to(asq_bsq[0].get_center()).set_opacity(0),
            FadeIn(asq_bsq[0]),
            ReplacementTransform(bsq, asq_bsq[1]),
            run_time=1.0
        )
        self.remove(a1, a2)

        self.wait(2.99)

        # Append = abba
        eq_append = MathTex("=").scale(1.1).next_to(asq_bsq, RIGHT, buff=0.35)
        abba_append = MathTex(r"\vec{a}", r"\vec{b}", r"\vec{b}", r"\vec{a}", arg_separator=r"\;").scale(1.1)
        abba_append.next_to(eq_append, RIGHT, buff=0.35)

        self.play(
            Write(eq_append),
            Write(abba_append),
            run_time=0.8
        )

        self.wait(2.51)

        # Line 3 expansion 
        line3_part1 = MathTex(r"(", r"\vec{a}", r" \cdot ", r"\vec{b}", r" + ", r"\vec{a}", r" \wedge ", r"\vec{b}", r")").scale(1.1)
        line3_part2 = MathTex(r"(", r"\vec{b}", r" \cdot ", r"\vec{a}", r" + ", r"\vec{b}", r" \wedge ", r"\vec{a}", r")").scale(1.1)
        
        line3 = VGroup(line3_part1, line3_part2).arrange(RIGHT, buff=0.15)
        line3.next_to(abba_append, DOWN, buff=0.4).align_to(abba_append, LEFT)

        # Create aligned equal sign for Line 3 
        eq_line2 = MathTex("=").scale(1.1)
        eq_line2.set_x(eq_append.get_x()).set_y(line3_part1.get_y())

        ab_source = VGroup(abba_append[0], abba_append[1]).copy()
        ba_source = VGroup(abba_append[2], abba_append[3]).copy()

        self.play(
            ReplacementTransform(ab_source, line3_part1), 
            Write(eq_line2),
            run_time=1.2
        )
        self.play(ReplacementTransform(ba_source, line3_part2), run_time=1.2)

        self.wait(4.30)

        # Slide b dot a -> a dot b
        b_vec1 = line3_part2[1]
        a_vec1 = line3_part2[3]
        pos_b1 = b_vec1.get_x()
        pos_a1 = a_vec1.get_x()

        self.play(
            b_vec1.animate.set_x(pos_a1),
            a_vec1.animate.set_x(pos_b1),
            run_time=0.8
        )

        self.wait(2.33)

        # Slide b wedge a -> a wedge b, + -> -
        plus_sign = line3_part2[4]
        minus_sign = MathTex("-").scale(1.1).move_to(plus_sign)
        b_vec2 = line3_part2[5]
        a_vec2 = line3_part2[7]
        pos_b2 = b_vec2.get_x()
        pos_a2 = a_vec2.get_x()

        self.play(
            b_vec2.animate.set_x(pos_a2),
            a_vec2.animate.set_x(pos_b2),
            ReplacementTransform(plus_sign, minus_sign),
            run_time=0.8
        )

        # We keep line3_part1 and line3_part2 unmodified visually to entirely prevent the jolt.
        # Track components directly for Line 4 assembly.
        src_adotb_left = VGroup(*line3_part1[1:4])
        src_plus_wedge_left = VGroup(*line3_part1[4:8])
        src_adotb_right = VGroup(line3_part2[3], line3_part2[2], line3_part2[1])
        src_minus_wedge_right = VGroup(minus_sign, line3_part2[7], line3_part2[6], line3_part2[5])

        self.wait(9.27)

        # ----------------------------------------------------
        # Line 4 Drop & Assembly (3:13:15 onwards)
        # ----------------------------------------------------
        # Term 1: (a \cdot b)^2
        L4_1 = MathTex(r"( \vec{a} \cdot \vec{b} )^2").scale(1.1)
        L4_1.align_to(line3_part1, LEFT).set_y(line3_part1.get_y() - line3_part1.height - 0.4)

        # Create aligned equal sign for Line 4 
        eq_line3 = MathTex("=").scale(1.1)
        eq_line3.set_x(eq_append.get_x()).set_y(L4_1.get_y())

        self.play(
            ReplacementTransform(src_adotb_left.copy(), L4_1),
            ReplacementTransform(src_adotb_right.copy(), L4_1),
            Write(eq_line3),
            run_time=1.2
        )

        self.wait(1.73)

        # Term 2: - (a \cdot b)(a \wedge b)
        L4_2 = MathTex(r"-", r"( \vec{a} \cdot \vec{b} )", r"( \vec{a} \wedge \vec{b} )").scale(1.1)
        L4_2.next_to(L4_1, RIGHT, buff=0.2)
        
        grp2 = VGroup(L4_2[0], L4_2[2])

        self.play(
            ReplacementTransform(src_adotb_left.copy(), L4_2[1]),
            ReplacementTransform(src_minus_wedge_right.copy(), grp2),
            run_time=1.2
        )
        self.add(*L4_2)

        self.wait(2.74)

        # Term 3: + (a \wedge b)(a \cdot b)
        L4_3 = MathTex(r"+", r"( \vec{a} \wedge \vec{b} )", r"( \vec{a} \cdot \vec{b} )").scale(1.1)
        L4_3.next_to(L4_2, RIGHT, buff=0.2)

        grp3 = VGroup(L4_3[0], L4_3[1])

        self.play(
            ReplacementTransform(src_plus_wedge_left.copy(), grp3),
            ReplacementTransform(src_adotb_right.copy(), L4_3[2]),
            run_time=1.2
        )
        self.add(*L4_3)

        self.wait(4.71)

        # ----------------------------------------------------
        # Factorisation Rigid Slide (3:26:02 onwards)
        # ----------------------------------------------------
        target_factored = MathTex(
            r"( \vec{a} \cdot \vec{b} )^2", 
            r"+", 
            r"( \vec{a} \cdot \vec{b} )", 
            r"\Big(", 
            r"-", 
            r"( \vec{a} \wedge \vec{b} )", 
            r"+", 
            r"( \vec{a} \wedge \vec{b} )", 
            r"\Big)"
        ).scale(1.1)
        
        target_factored.align_to(L4_1, LEFT).set_y(L4_1.get_y())

        self.play(
            FadeIn(target_factored[1]),
            L4_2[1].animate.move_to(target_factored[2]),
            L4_3[2].animate.move_to(target_factored[2]),
            FadeIn(target_factored[3]),
            L4_2[0].animate.move_to(target_factored[4]),
            L4_2[2].animate.move_to(target_factored[5]),
            L4_3[0].animate.move_to(target_factored[6]),
            L4_3[1].animate.move_to(target_factored[7]),
            FadeIn(target_factored[8]),
            run_time=1.2
        )
        
        self.remove(*L4_2, *L4_3)
        self.add(*target_factored[1:])

        self.wait(1.10)

        # ----------------------------------------------------
        # Cancellation and Vanish (3:28:20 onwards)
        # ----------------------------------------------------
        left_wedge_term = VGroup(target_factored[4], target_factored[5])
        right_wedge_term = VGroup(target_factored[6], target_factored[7])
        slide_center = VGroup(left_wedge_term, right_wedge_term).get_center()

        left_shift = slide_center - left_wedge_term.get_center()
        right_shift = slide_center - right_wedge_term.get_center()

        self.play(
            FadeOut(target_factored[4], shift=left_shift),
            FadeOut(target_factored[5], shift=left_shift),
            FadeOut(target_factored[6], shift=right_shift),
            FadeOut(target_factored[7], shift=right_shift),
            FadeOut(target_factored[1]),
            FadeOut(target_factored[2]),
            FadeOut(target_factored[3]),
            FadeOut(target_factored[8]),
            run_time=1.0
        )

        self.wait(1.84)

        # ----------------------------------------------------
        # t = 67.17s (3:31:10 on timeline): Drop remaining wedge terms 
        # ----------------------------------------------------
        L4_4 = MathTex(r"-", r"( \vec{a} \wedge \vec{b} )^2").scale(1.1)
        L4_4.next_to(L4_1, RIGHT, buff=0.2)

        self.play(
            ReplacementTransform(VGroup(src_plus_wedge_left.copy(), src_minus_wedge_right.copy()), L4_4),
            run_time=1.2
        )

        self.wait(0.86)

        # ----------------------------------------------------
        # t = 69.23s (3:33:12 on timeline): Reformatting lines
        # ----------------------------------------------------
        target_y = line3_part1.get_y()

        self.play(
            # Carefully clear Line 3 visually via explicit extraction 
            FadeOut(VGroup(
                *line3_part1, 
                *line3_part2[:4], 
                *line3_part2[5:], 
                minus_sign, 
                eq_line2
            )),
            
            L4_1.animate.set_y(target_y),
            L4_4.animate.set_y(target_y),
            eq_line3.animate.set_y(target_y),
            
            asq_bsq.animate.set_y(target_y),
            abba_append.animate.next_to(eq_append, LEFT, buff=0.35),
            
            run_time=1.2
        )

        # Tail buffer for timeline expansion
        self.wait(10.00)
        

class Scene8(Scene):
    def construct(self):
        # ----------------------------------------------------
        # Recreate Scene 7 Final Frame Setup
        # ----------------------------------------------------
        ab_lhs = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1).move_to(LEFT * 5.0 + UP * 2.2)
        eq_sign_2 = MathTex("=").scale(1.1).next_to(ab_lhs, RIGHT, buff=0.35)

        ab1 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab1 = MathTex("2").scale(1.1)
        bar_ab1 = Line(ORIGIN, RIGHT * (ab1.width + 0.2), stroke_width=2)
        ab1.next_to(bar_ab1, UP, buff=0.15)
        den_ab1.next_to(bar_ab1, DOWN, buff=0.15)
        frac1_dummy = VGroup(ab1, bar_ab1, den_ab1).next_to(eq_sign_2, RIGHT, buff=0.35)

        plus_mid = MathTex("+").scale(1.1).next_to(frac1_dummy, RIGHT, buff=0.35)

        ab2 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab2 = MathTex("2").scale(1.1)
        bar_ab2 = Line(ORIGIN, RIGHT * (ab2.width + 0.2), stroke_width=2)
        ab2.next_to(bar_ab2, UP, buff=0.15)
        den_ab2.next_to(bar_ab2, DOWN, buff=0.15)
        frac2_dummy = VGroup(ab2, bar_ab2, den_ab2).next_to(plus_mid, RIGHT, buff=0.35)

        plus0 = MathTex("+").scale(1.1).next_to(frac2_dummy, RIGHT, buff=0.4)
        ba1 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)
        
        minus_ba = MathTex("-").scale(1.1)
        ba2 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)

        dum_num_L = VGroup(ab1.copy(), plus0.copy(), ba1.copy()).arrange(RIGHT, buff=0.25)
        dum_num_L.shift(ab1.get_center() - dum_num_L[0].get_center())

        t_bar_L = Line(dum_num_L.get_left() + LEFT * 0.1, dum_num_L.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_L.set_y(bar_ab1.get_y())
        t_den_L = den_ab1.copy().set_x(t_bar_L.get_x())

        shift_amount = t_bar_L.get_right()[0] - bar_ab1.get_right()[0]
        plus_mid.shift(RIGHT * shift_amount)
        frac2_dummy.shift(RIGHT * shift_amount)

        dum_num_R = VGroup(ab2.copy(), minus_ba.copy(), ba2.copy()).arrange(RIGHT, buff=0.25)
        dum_num_R.shift(ab2.get_center() - dum_num_R[0].get_center())

        t_bar_R = Line(dum_num_R.get_left() + LEFT * 0.1, dum_num_R.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_R.set_y(bar_ab2.get_y())
        t_den_R = den_ab2.copy().set_x(t_bar_R.get_x())

        ab1.move_to(dum_num_L[0])
        plus0.move_to(dum_num_L[1])
        ba1.move_to(dum_num_L[2])
        frac_L = VGroup(ab1, plus0, ba1, t_bar_L, t_den_L)

        ab2.move_to(dum_num_R[0])
        minus_ba.move_to(dum_num_R[1])
        ba2.move_to(dum_num_R[2])
        frac_R = VGroup(ab2, minus_ba, ba2, t_bar_R, t_den_R)

        dot_term = MathTex(r"\vec{a} \cdot \vec{b}").scale(1.1).move_to(frac_L)
        wedge_term = MathTex(r"\vec{a} \wedge \vec{b}").scale(1.1).move_to(frac_R)

        self.add(ab_lhs, eq_sign_2, dot_term, plus_mid, wedge_term)

        # ----------------------------------------------------
        # Reconstruct Scene 7 alignment structure perfectly 
        # using identical VGroup parameters to fix the Y jolt.
        # ----------------------------------------------------
        line2_y = ab_lhs.get_y() - 1.5

        dummy_asq_bsq = MathTex(r"a^2", r"b^2", arg_separator=r"\;").scale(1.1)
        dummy_asq_bsq.align_to(ab_lhs, LEFT).set_y(line2_y)

        dummy_eq = MathTex("=").scale(1.1).next_to(dummy_asq_bsq, RIGHT, buff=0.35)
        
        dummy_abba = MathTex(r"\vec{a}", r"\vec{b}", r"\vec{b}", r"\vec{a}", arg_separator=r"\;").scale(1.1)
        dummy_abba.next_to(dummy_eq, RIGHT, buff=0.35)

        d_line3_1 = MathTex(r"(", r"\vec{a}", r" \cdot ", r"\vec{b}", r" + ", r"\vec{a}", r" \wedge ", r"\vec{b}", r")").scale(1.1)
        d_line3_2 = MathTex(r"(", r"\vec{b}", r" \cdot ", r"\vec{a}", r" + ", r"\vec{b}", r" \wedge ", r"\vec{a}", r")").scale(1.1)
        d_line3 = VGroup(d_line3_1, d_line3_2).arrange(RIGHT, buff=0.15)
        d_line3.next_to(dummy_abba, DOWN, buff=0.4).align_to(dummy_abba, LEFT)

        target_y = d_line3_1.get_y()

        # ----------------------------------------------------
        # Persistent Line 2 components (Static Background)
        # ----------------------------------------------------
        eq_append = MathTex("=").scale(1.1).set_x(dummy_eq.get_x()).set_y(line2_y)
        abba_append = MathTex(r"\vec{a}", r"\vec{b}", r"\vec{b}", r"\vec{a}", arg_separator=r"\;").scale(1.1)
        abba_append.next_to(eq_append, LEFT, buff=0.35).set_y(line2_y)
        self.add(eq_append, abba_append)

        # ----------------------------------------------------
        # Scene 8 Active Equation Initial State 
        # ----------------------------------------------------
        asq_bsq = MathTex(r"a^2", r"b^2", arg_separator=r"\;").scale(1.1)
        asq_bsq.align_to(ab_lhs, LEFT).set_y(target_y)

        eq_line3 = MathTex("=").scale(1.1).set_x(dummy_eq.get_x()).set_y(target_y)

        L4_1 = MathTex(r"( \vec{a} \cdot \vec{b} )^2").scale(1.1)
        L4_1.align_to(d_line3_1, LEFT).set_y(target_y)

        L4_4 = MathTex(r"-", r"( \vec{a} \wedge \vec{b} )^2").scale(1.1)
        L4_4.next_to(L4_1, RIGHT, buff=0.2).set_y(target_y)

        self.add(asq_bsq, eq_line3, L4_1, L4_4)

        asq1 = asq_bsq[0]
        bsq1 = asq_bsq[1]
        minus_rhs = L4_4[0]
        awedge_sq = L4_4[1]

        # ----------------------------------------------------
        # Timeline Alignment (Start: 3:34:20 -> t = 0.00s)
        # ----------------------------------------------------
        self.wait(1.00)

        # ----------------------------------------------------
        # t = 1.00s (3:35:12): (a dot b)^2 -> a^2 b^2 cos^2 theta
        # ----------------------------------------------------
        asq2 = MathTex(r"a^2").scale(1.1)
        bsq2 = MathTex(r"b^2").scale(1.1)
        cos2 = MathTex(r"\cos^2 \theta").scale(1.1)
        
        a2b2_cos2 = VGroup(asq2, bsq2, cos2).arrange(RIGHT, buff=0.1)
        a2b2_cos2.next_to(eq_line3, RIGHT, buff=0.35).set_y(target_y)
        
        tgt_L4_4 = MathTex(r"-", r"( \vec{a} \wedge \vec{b} )^2").scale(1.1)
        tgt_L4_4.next_to(a2b2_cos2, RIGHT, buff=0.2).set_y(target_y)

        self.play(
            ReplacementTransform(L4_1, a2b2_cos2),
            minus_rhs.animate.move_to(tgt_L4_4[0]),
            awedge_sq.animate.move_to(tgt_L4_4[1]),
            run_time=1.0
        )

        self.wait(1.20)

        # ----------------------------------------------------
        # t = 3.20s (3:37:23): Move to Left of Equation (Rigid shift)
        # ----------------------------------------------------
        lhs_minus = MathTex("-").scale(1.1)
        
        line2_lhs = VGroup(
            MathTex(r"a^2").scale(1.1), MathTex(r"b^2").scale(1.1),
            MathTex("-").scale(1.1),
            MathTex(r"a^2").scale(1.1), MathTex(r"b^2").scale(1.1), MathTex(r"\cos^2 \theta").scale(1.1)
        )
        
        line2_lhs[0].move_to(ORIGIN)
        for i in range(1, len(line2_lhs)):
            buff_val = 0.35 if i in [2, 3] else 0.1
            line2_lhs[i].next_to(line2_lhs[i-1], RIGHT, buff=buff_val)
            
        line2_lhs.align_to(ab_lhs, LEFT).set_y(target_y)

        tgt_eq2 = MathTex("=").scale(1.1).next_to(line2_lhs, RIGHT, buff=0.35).set_y(target_y)
        tgt_L4_4_v2 = MathTex(r"-", r"( \vec{a} \wedge \vec{b} )^2").scale(1.1).next_to(tgt_eq2, RIGHT, buff=0.35).set_y(target_y)

        self.play(
            asq1.animate.move_to(line2_lhs[0]),
            bsq1.animate.move_to(line2_lhs[1]),
            FadeIn(lhs_minus.move_to(line2_lhs[2])),
            asq2.animate.move_to(line2_lhs[3]),
            bsq2.animate.move_to(line2_lhs[4]),
            cos2.animate.move_to(line2_lhs[5]),
            eq_line3.animate.move_to(tgt_eq2),
            minus_rhs.animate.move_to(tgt_L4_4_v2[0]),
            awedge_sq.animate.move_to(tgt_L4_4_v2[1]),
            run_time=1.2
        )

        self.wait(1.50)

        # ----------------------------------------------------
        # t = 5.90s (3:40:07): Factorise to a^2 b^2 (1 - cos^2 theta)
        # ----------------------------------------------------
        l_paren = MathTex("(").scale(1.1)
        one_tex = MathTex("1").scale(1.1)
        r_paren = MathTex(")").scale(1.1)

        line3_lhs = VGroup(
            MathTex(r"a^2").scale(1.1), MathTex(r"b^2").scale(1.1),
            MathTex("(").scale(1.1), MathTex("1").scale(1.1), MathTex("-").scale(1.1), MathTex(r"\cos^2 \theta").scale(1.1), MathTex(")").scale(1.1)
        )
        
        line3_lhs[0].move_to(ORIGIN)
        buffs = [0.1, 0.15, 0.1, 0.25, 0.25, 0.1]
        for i in range(1, len(line3_lhs)):
            line3_lhs[i].next_to(line3_lhs[i-1], RIGHT, buff=buffs[i-1])

        line3_lhs.align_to(ab_lhs, LEFT).set_y(target_y)

        tgt_eq3 = MathTex("=").scale(1.1).next_to(line3_lhs, RIGHT, buff=0.35).set_y(target_y)
        tgt_L4_4_v3 = MathTex(r"-", r"( \vec{a} \wedge \vec{b} )^2").scale(1.1).next_to(tgt_eq3, RIGHT, buff=0.35).set_y(target_y)

        self.play(
            asq1.animate.move_to(line3_lhs[0]),
            bsq1.animate.move_to(line3_lhs[1]),
            asq2.animate.move_to(line3_lhs[0]), 
            bsq2.animate.move_to(line3_lhs[1]), 
            FadeIn(l_paren.move_to(line3_lhs[2])),
            FadeIn(one_tex.move_to(line3_lhs[3])),
            lhs_minus.animate.move_to(line3_lhs[4]),
            cos2.animate.move_to(line3_lhs[5]),
            FadeIn(r_paren.move_to(line3_lhs[6])),
            eq_line3.animate.move_to(tgt_eq3),
            minus_rhs.animate.move_to(tgt_L4_4_v3[0]),
            awedge_sq.animate.move_to(tgt_L4_4_v3[1]),
            run_time=1.2
        )
        
        self.remove(asq2, bsq2)

        self.wait(0.90)

        # ----------------------------------------------------
        # t = 8.00s (3:42:13): (1 - cos^2 theta) -> sin^2 theta
        # ----------------------------------------------------
        sin2 = MathTex(r"\sin^2 \theta").scale(1.1)

        line4_lhs = VGroup(
            MathTex(r"a^2").scale(1.1), MathTex(r"b^2").scale(1.1), MathTex(r"\sin^2 \theta").scale(1.1)
        ).arrange(RIGHT, buff=0.1)
        line4_lhs[2].next_to(line4_lhs[1], RIGHT, buff=0.15)
        
        line4_lhs.align_to(ab_lhs, LEFT).set_y(target_y)

        tgt_eq4 = MathTex("=").scale(1.1).next_to(line4_lhs, RIGHT, buff=0.35).set_y(target_y)
        tgt_L4_4_v4 = MathTex(r"-", r"( \vec{a} \wedge \vec{b} )^2").scale(1.1).next_to(tgt_eq4, RIGHT, buff=0.35).set_y(target_y)

        sin2.move_to(line4_lhs[2])

        self.play(
            asq1.animate.move_to(line4_lhs[0]),
            bsq1.animate.move_to(line4_lhs[1]),
            ReplacementTransform(VGroup(l_paren, one_tex, lhs_minus, cos2, r_paren), sin2),
            eq_line3.animate.move_to(tgt_eq4),
            minus_rhs.animate.move_to(tgt_L4_4_v4[0]),
            awedge_sq.animate.move_to(tgt_L4_4_v4[1]),
            run_time=1.2
        )

        self.wait(1.20)

        # ----------------------------------------------------
        # t = 10.40s: Swap Left and Right Hands smoothly via Path Arc
        # ----------------------------------------------------
        final_lhs = MathTex(r"( \vec{a} \wedge \vec{b} )^2").scale(1.1)
        final_eq = MathTex("=").scale(1.1)
        final_minus = MathTex("-").scale(1.1)
        final_rhs = MathTex(r"(", r"a b \sin \theta", r")^2").scale(1.1)

        final_group = VGroup(final_lhs, final_eq, final_minus, final_rhs).arrange(RIGHT, buff=0.35)
        final_group[3].next_to(final_group[2], RIGHT, buff=0.2) 
        
        current_center_x = VGroup(line4_lhs, tgt_eq4, tgt_L4_4_v4).get_center()[0]
        final_group.move_to(np.array([current_center_x, line2_y, 0]))

        final_lhs.move_to(final_group[0])
        final_eq.move_to(final_group[1])
        final_minus.move_to(final_group[2])
        final_rhs.move_to(final_group[3])

        self.play(
            awedge_sq.animate(path_arc=PI/2).move_to(final_lhs),
            ReplacementTransform(VGroup(asq1, bsq1, sin2), final_rhs, path_arc=PI/2),
            eq_line3.animate.move_to(final_eq),
            minus_rhs.animate.move_to(final_minus),
            FadeOut(abba_append),
            FadeOut(eq_append),
            run_time=1.5
        )

        # ----------------------------------------------------
        # Smoothed Brace Flow
        # t = 21.20s: Wait ends
        # ----------------------------------------------------
        self.wait(9.30) 

        # Brace under ab \sin \theta
        brace1 = Brace(final_rhs[1], DOWN, buff=0.1)
        label1 = MathTex(r"\mathbb{R}").scale(1.1).next_to(brace1, DOWN, buff=0.1)
        
        self.play(GrowFromCenter(brace1), FadeIn(label1), run_time=0.8)
        self.wait(0.30)

        # Brace expands to include squares
        brace2 = Brace(final_rhs, DOWN, buff=0.1)
        label2 = MathTex(r"\mathbb{R}_{\ge 0}").scale(1.1).next_to(brace2, DOWN, buff=0.1)
        
        self.play(ReplacementTransform(brace1, brace2), ReplacementTransform(label1, label2), run_time=0.8)
        self.wait(0.30)

        # Brace expands to include negative sign (finishes at t = 24.20s)
        brace3 = Brace(VGroup(final_minus, final_rhs), DOWN, buff=0.1)
        label3 = MathTex(r"\mathbb{R}_{\le 0}").scale(1.1).next_to(brace3, DOWN, buff=0.1)
        
        self.play(ReplacementTransform(brace2, brace3), ReplacementTransform(label2, label3), run_time=0.8)
        
        # ----------------------------------------------------
        # t = 27.92s (4:02:15 on timeline): Write implication line
        # 27.92s - 24.20s = 3.72s
        # ----------------------------------------------------
        self.wait(3.72)

        imp_line = MathTex(r"\implies \vec{a} \wedge \vec{b} \notin \mathbb{R}").scale(1.1)
        imp_line.align_to(ab_lhs, LEFT).set_y(label3.get_y() - 2.0)
        
        self.play(Write(imp_line), run_time=0.8)

        # ----------------------------------------------------
        # t = 31.72s (4:06:03 on timeline): Write vector magnitude line
        # 31.72s - (27.92s + 0.8s) = 3.00s
        # ----------------------------------------------------
        self.wait(3.00)

        mid_line = MathTex(r"{\vec{v}}^{\,2} = |\vec{v}|^2 \in \mathbb{R}_{\ge 0}").scale(1.1)
        mid_line.align_to(ab_lhs, LEFT).set_y(label3.get_y() - 1.0)
        
        self.play(Write(mid_line), run_time=0.8)

        # ----------------------------------------------------
        # t = 34.05s (4:08:23 on timeline): Append \notin V to implication line
        # 34.05s - (31.72s + 0.8s) = 1.53s
        # ----------------------------------------------------
        self.wait(1.53)

        imp_append = MathTex(r",\; \vec{a} \wedge \vec{b} \notin V").scale(1.1)
        imp_append.next_to(imp_line, RIGHT, buff=0.15)
        
        self.play(Write(imp_append), run_time=0.8)

        # Tail buffer for timeline expansion
        self.wait(10.00)
        
        
class Scene9(Scene):
    def construct(self):
        # ----------------------------------------------------
        # Recreate Scene 8 Final Frame Setup Exactly
        # ----------------------------------------------------
        ab_lhs = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1).move_to(LEFT * 5.0 + UP * 2.2)
        eq_sign_2 = MathTex("=").scale(1.1).next_to(ab_lhs, RIGHT, buff=0.35)

        ab1 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab1 = MathTex("2").scale(1.1)
        bar_ab1 = Line(ORIGIN, RIGHT * (ab1.width + 0.2), stroke_width=2)
        ab1.next_to(bar_ab1, UP, buff=0.15)
        den_ab1.next_to(bar_ab1, DOWN, buff=0.15)
        frac1_dummy = VGroup(ab1, bar_ab1, den_ab1).next_to(eq_sign_2, RIGHT, buff=0.35)

        plus_mid = MathTex("+").scale(1.1).next_to(frac1_dummy, RIGHT, buff=0.35)

        ab2 = MathTex(r"\vec{a}", r"\vec{b}", arg_separator="").scale(1.1)
        den_ab2 = MathTex("2").scale(1.1)
        bar_ab2 = Line(ORIGIN, RIGHT * (ab2.width + 0.2), stroke_width=2)
        ab2.next_to(bar_ab2, UP, buff=0.15)
        den_ab2.next_to(bar_ab2, DOWN, buff=0.15)
        frac2_dummy = VGroup(ab2, bar_ab2, den_ab2).next_to(plus_mid, RIGHT, buff=0.35)

        plus0 = MathTex("+").scale(1.1).next_to(frac2_dummy, RIGHT, buff=0.4)
        ba1 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)
        
        minus_ba = MathTex("-").scale(1.1)
        ba2 = MathTex(r"\vec{b}", r"\vec{a}", arg_separator="").scale(1.1)

        dum_num_L = VGroup(ab1.copy(), plus0.copy(), ba1.copy()).arrange(RIGHT, buff=0.25)
        dum_num_L.shift(ab1.get_center() - dum_num_L[0].get_center())

        t_bar_L = Line(dum_num_L.get_left() + LEFT * 0.1, dum_num_L.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_L.set_y(bar_ab1.get_y())
        t_den_L = den_ab1.copy().set_x(t_bar_L.get_x())

        shift_amount = t_bar_L.get_right()[0] - bar_ab1.get_right()[0]
        plus_mid.shift(RIGHT * shift_amount)
        frac2_dummy.shift(RIGHT * shift_amount)

        dum_num_R = VGroup(ab2.copy(), minus_ba.copy(), ba2.copy()).arrange(RIGHT, buff=0.25)
        dum_num_R.shift(ab2.get_center() - dum_num_R[0].get_center())

        t_bar_R = Line(dum_num_R.get_left() + LEFT * 0.1, dum_num_R.get_right() + RIGHT * 0.1, stroke_width=2)
        t_bar_R.set_y(bar_ab2.get_y())
        t_den_R = den_ab2.copy().set_x(t_bar_R.get_x())

        ab1.move_to(dum_num_L[0])
        plus0.move_to(dum_num_L[1])
        ba1.move_to(dum_num_L[2])
        frac_L = VGroup(ab1, plus0, ba1, t_bar_L, t_den_L)

        ab2.move_to(dum_num_R[0])
        minus_ba.move_to(dum_num_R[1])
        ba2.move_to(dum_num_R[2])
        frac_R = VGroup(ab2, minus_ba, ba2, t_bar_R, t_den_R)

        dot_term = MathTex(r"\vec{a} \cdot \vec{b}").scale(1.1).move_to(frac_L)
        wedge_term = MathTex(r"\vec{a} \wedge \vec{b}").scale(1.1).move_to(frac_R)

        line1_group = VGroup(ab_lhs, eq_sign_2, dot_term, plus_mid, wedge_term)

        dummy_abba = MathTex(r"\vec{a}", r"\vec{b}", r"\vec{b}", r"\vec{a}", arg_separator=r"\;").scale(1.1)
        dummy_abba.align_to(ab_lhs, LEFT).set_y(ab_lhs.get_y() - 1.5)
        dummy_line3 = MathTex(r"(", r"\vec{a}", r" \cdot ", r"\vec{b}", r" + ", r"\vec{a}", r" \wedge ", r"\vec{b}", r")").scale(1.1)
        dummy_line3.next_to(dummy_abba, DOWN, buff=0.4).align_to(dummy_abba, LEFT)
        
        target_y = dummy_line3.get_y()
        line2_y = ab_lhs.get_y() - 1.5

        line4_lhs = VGroup(
            MathTex(r"a^2").scale(1.1), MathTex(r"b^2").scale(1.1), MathTex(r"\sin^2 \theta").scale(1.1)
        ).arrange(RIGHT, buff=0.1)
        line4_lhs[2].next_to(line4_lhs[1], RIGHT, buff=0.15)
        line4_lhs.align_to(ab_lhs, LEFT).set_y(target_y)

        tgt_eq4 = MathTex("=").scale(1.1).next_to(line4_lhs, RIGHT, buff=0.35).set_y(target_y)
        tgt_L4_4_v4 = MathTex(r"-", r"( \vec{a} \wedge \vec{b} )^2").scale(1.1).next_to(tgt_eq4, RIGHT, buff=0.35).set_y(target_y)
        current_center_x = VGroup(line4_lhs, tgt_eq4, tgt_L4_4_v4).get_center()[0]

        final_lhs = MathTex(r"( \vec{a} \wedge \vec{b} )^2").scale(1.1)
        final_eq = MathTex("=").scale(1.1)
        final_minus = MathTex("-").scale(1.1)
        final_rhs = MathTex(r"(", r"a b \sin \theta", r")^2").scale(1.1)

        final_group = VGroup(final_lhs, final_eq, final_minus, final_rhs).arrange(RIGHT, buff=0.35)
        final_group[3].next_to(final_group[2], RIGHT, buff=0.2) 
        final_group.move_to(np.array([current_center_x, line2_y, 0]))

        final_lhs.move_to(final_group[0])
        final_eq.move_to(final_group[1])
        final_minus.move_to(final_group[2])
        final_rhs.move_to(final_group[3])

        brace3 = Brace(VGroup(final_minus, final_rhs), DOWN, buff=0.1)
        label3 = MathTex(r"\mathbb{R}_{\le 0}").scale(1.1).next_to(brace3, DOWN, buff=0.1)

        imp_line = MathTex(r"\implies \vec{a} \wedge \vec{b} \notin \mathbb{R}").scale(1.1)
        imp_line.align_to(ab_lhs, LEFT).set_y(label3.get_y() - 2.0)
        
        mid_line = MathTex(r"{\vec{v}}^{\,2} = |\vec{v}|^2 \in \mathbb{R}_{\ge 0}").scale(1.1)
        mid_line.align_to(ab_lhs, LEFT).set_y(label3.get_y() - 1.0)
        
        imp_append = MathTex(r",\; \vec{a} \wedge \vec{b} \notin V").scale(1.1)
        imp_append.next_to(imp_line, RIGHT, buff=0.15)

        self.add(
            line1_group, 
            final_lhs, final_eq, final_minus, final_rhs, 
            brace3, label3, 
            imp_line, mid_line, imp_append
        )

        # ----------------------------------------------------
        # t = 0.00s (4:10:14): Start Scene 9
        # ----------------------------------------------------
        
        # ----------------------------------------------------
        # t = 2.76s (4:13:00): Fade out background, Line 2 rises to Line 1
        # ----------------------------------------------------
        self.wait(2.76)

        moving_group = VGroup(final_lhs, final_eq, final_minus, final_rhs)
        
        shift_vector = np.array([
            ab_lhs.get_left()[0] - final_lhs.get_left()[0],
            ab_lhs.get_y() - final_lhs.get_y(),
            0
        ])
        
        self.play(
            FadeOut(line1_group),
            FadeOut(brace3),
            FadeOut(label3),
            FadeOut(imp_line),
            FadeOut(mid_line),
            FadeOut(imp_append),
            moving_group.animate.shift(shift_vector),
            run_time=1.2
        )

        # ----------------------------------------------------
        # t = 5.88s (4:16:07): Write out new equation
        # ----------------------------------------------------
        self.wait(1.92)

        line2_new = MathTex(r"\vec{a} \wedge \vec{b}", r"\overset{?}{=}", r"\alpha + \beta i").scale(1.1)
        line2_new.align_to(ab_lhs, LEFT).set_y(ab_lhs.get_y() - 1.5)

        self.play(Write(line2_new), run_time=1.0)

        # ----------------------------------------------------
        # t = 9.05s (4:19:17): Red Cross draws over alpha + beta i
        # ----------------------------------------------------
        self.wait(2.17)

        red_cross = Cross(line2_new[2], stroke_color=RED, stroke_width=6)
        
        self.play(Create(red_cross), run_time=0.8)

        # ----------------------------------------------------
        # t = 12.06s (4:22:18): Diagram of a and b drawn
        # ----------------------------------------------------
        self.wait(2.21)

        a_wedge_b = line2_new[0]
        target_pos = UP * 2.8 + LEFT * 5.0

        diagram_start = np.array([0.5, -0.2, 0])
        vec_b_end = diagram_start + RIGHT * 2.7
        vec_a_end = diagram_start + RIGHT * 1.4 + UP * 1.9

        pink_color = "#FF66B2"
        purple_color = "#A468FF"
        cyan_color = "#00FFFF"
        
        vec_b = Arrow(diagram_start, vec_b_end, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=0.07)
        vec_a = Arrow(diagram_start, vec_a_end, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=0.08)

        label_b = MathTex(r"\vec{b}", color=purple_color).scale(1.1).next_to(vec_b.get_end(), DOWN, buff=0.15)
        label_a = MathTex(r"\vec{a}", color=pink_color).scale(1.1).next_to(vec_a.get_end(), UP, buff=0.15)

        angle = Angle(vec_b, vec_a, radius=0.6, color=cyan_color, stroke_width=4)
        theta = MathTex(r"\theta", color=cyan_color).scale(0.95).move_to(diagram_start + RIGHT * 0.85 + UP * 0.28)
        
        angle_group = VGroup(angle, theta)
        angle_group.save_state()

        self.play(
            a_wedge_b.animate.move_to(target_pos),
            FadeOut(line2_new[1]),
            FadeOut(line2_new[2]),
            FadeOut(red_cross),
            FadeOut(moving_group),
            run_time=1.2
        )

        self.play(
            GrowArrow(vec_b),
            GrowArrow(vec_a),
            run_time=0.8
        )
        
        self.play(
            Write(label_b),
            Write(label_a),
            Create(angle),
            Write(theta),
            run_time=0.8
        )

        # ----------------------------------------------------
        # t = 17.82s (4:28:03): Closing of a and b (slow and smooth)
        # ----------------------------------------------------
        self.wait(2.96)

        vec_a_shadow_end = np.array([vec_a_end[0], diagram_start[1], 0])

        self.play(
            vec_a.animate.put_start_and_end_on(diagram_start, vec_a_shadow_end),
            label_a.animate.next_to(vec_a_shadow_end, UP, buff=0.15),
            angle_group.animate.scale([1, 0.0001, 1], about_point=diagram_start).set_opacity(0),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 19.32s: Open back up
        # ----------------------------------------------------
        self.wait(0.5)

        self.play(
            vec_a.animate.put_start_and_end_on(diagram_start, vec_a_end),
            label_a.animate.next_to(vec_a_end, UP, buff=0.15),
            Restore(angle_group),
            run_time=1.0
        )

        # ----------------------------------------------------
        # Orange parallelogram 1 appears
        # ----------------------------------------------------
        self.wait(0.2) 

        top_right_corner = vec_a_end + (vec_b_end - diagram_start)
        
        parallelogram = Polygon(
            diagram_start,
            vec_a_end,
            top_right_corner,
            vec_b_end,
            fill_color=ORANGE,
            fill_opacity=0.0,
            stroke_width=0
        )
        self.add(parallelogram)

        self.play(
            parallelogram.animate.set_fill(opacity=0.18),
            run_time=1.0
        )

        # ----------------------------------------------------
        # Vector b slides, then edges grow
        # ----------------------------------------------------
        self.wait(2.35) 
        
        shift_vector_b = vec_a_end - diagram_start

        self.play(
            vec_b.animate.shift(shift_vector_b),
            label_b.animate.shift(shift_vector_b),
            run_time=0.7
        )

        pink_edge = Arrow(
            top_right_corner, 
            vec_b_end, 
            buff=0, 
            color=pink_color, 
            stroke_width=6, 
            max_tip_length_to_length_ratio=0.08
        )
        
        self.play(GrowArrow(pink_edge), run_time=1.0)

        purple_edge = Arrow(
            vec_b_end, 
            diagram_start, 
            buff=0, 
            color=purple_color, 
            stroke_width=6, 
            max_tip_length_to_length_ratio=0.07
        )

        self.play(GrowArrow(purple_edge), run_time=1.0)

        # ----------------------------------------------------
        # t = 30.01s (4:40:15): Blue text ab sin theta appears
        # ----------------------------------------------------
        self.wait(3.44)

        para_text = MathTex(r"ab \sin \theta", color=BLUE).scale(0.9)
        para_text.move_to(parallelogram.get_center())

        self.play(FadeIn(para_text), run_time=0.8)

        # ----------------------------------------------------
        # t = 42.00s (4:52:14): Draw second parallelogram
        # ----------------------------------------------------
        self.wait(11.19)

        p2_start = np.array([-4.0, -0.2, 0])
        p2_b_end = p2_start + RIGHT * 2.7
        p2_top_right = p2_b_end + RIGHT * 1.4 + UP * 1.9
        p2_top_left = p2_start + RIGHT * 1.4 + UP * 1.9

        vec_b2 = Arrow(p2_start, p2_b_end, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=0.07)
        label_b2 = MathTex(r"\vec{b}", color=purple_color).scale(1.1).next_to(vec_b2.get_end(), DOWN, buff=0.15)

        self.play(
            GrowArrow(vec_b2),
            Write(label_b2),
            run_time=0.8
        )

        vec_a2 = Arrow(p2_b_end, p2_top_right, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=0.08)
        label_a2 = MathTex(r"\vec{a}", color=pink_color).scale(1.1).next_to(p2_top_right, RIGHT, buff=0.15)

        self.play(
            GrowArrow(vec_a2),
            Write(label_a2),
            run_time=0.8
        )

        vec_top2 = Arrow(p2_top_right, p2_top_left, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=0.07)

        self.play(
            GrowArrow(vec_top2),
            run_time=0.8
        )

        vec_left2 = Arrow(p2_top_left, p2_start, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=0.08)

        parallelogram2 = Polygon(
            p2_start,
            p2_top_left,
            p2_top_right,
            p2_b_end,
            fill_color=ORANGE,
            fill_opacity=0.0,
            stroke_width=0
        )
        self.add(parallelogram2)

        self.play(
            GrowArrow(vec_left2),
            parallelogram2.animate.set_fill(opacity=0.18),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 48.87s (4:59:01): Circulate standalone arrowheads
        # ----------------------------------------------------
        self.wait(3.47)

        # Define perimeter points for interpolation
        C0 = diagram_start
        C1 = vec_a_end
        C2 = top_right_corner
        C3 = vec_b_end

        D0 = p2_start
        D1 = p2_b_end
        D2 = p2_top_right
        D3 = p2_top_left

        # Generate fixed static lines to replace the bodies
        l_p1_a = Line(C0, C1, color=pink_color, stroke_width=6)
        l_p1_b = Line(C1, C2, color=purple_color, stroke_width=6)
        l_p1_r = Line(C2, C3, color=pink_color, stroke_width=6)
        l_p1_d = Line(C3, C0, color=purple_color, stroke_width=6)

        l_p2_b = Line(D0, D1, color=purple_color, stroke_width=6)
        l_p2_a = Line(D1, D2, color=pink_color, stroke_width=6)
        l_p2_t = Line(D2, D3, color=purple_color, stroke_width=6)
        l_p2_l = Line(D3, D0, color=pink_color, stroke_width=6)

        fixed_lines = VGroup(l_p1_a, l_p1_b, l_p1_r, l_p1_d, l_p2_b, l_p2_a, l_p2_t, l_p2_l)

        # Create unrendered dummy arrows to extract perfectly scaled native tips
        len_a = np.linalg.norm(C1 - C0)
        len_b = np.linalg.norm(C3 - C0)
        dummy_a = Arrow(ORIGIN, RIGHT * len_a, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.08)
        dummy_b = Arrow(ORIGIN, RIGHT * len_b, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.07)

        # Interpolation functions mapping a continuous value (0 to 4) to (position, tangency, is_a_vector_boolean)
        def get_p1_state(u):
            u = u % 4.0
            if u == 0: u = 4.0
            if u <= 1.0: return C0 * (1 - u) + C1 * u, Line(C0, C1).get_angle(), True
            elif u <= 2.0: return C1 * (2 - u) + C2 * (u - 1), Line(C1, C2).get_angle(), False
            elif u <= 3.0: return C2 * (3 - u) + C3 * (u - 2), Line(C2, C3).get_angle(), True
            else: return C3 * (4 - u) + C0 * (u - 3), Line(C3, C0).get_angle(), False

        def get_p2_state(u):
            u = u % 4.0
            if u == 0: u = 4.0
            if u <= 1.0: return D0 * (1 - u) + D1 * u, Line(D0, D1).get_angle(), False
            elif u <= 2.0: return D1 * (2 - u) + D2 * (u - 1), Line(D1, D2).get_angle(), True
            elif u <= 3.0: return D2 * (3 - u) + D3 * (u - 2), Line(D2, D3).get_angle(), False
            else: return D3 * (4 - u) + D0 * (u - 3), Line(D3, D0).get_angle(), True

        # Copy the native tip and place it accurately for horizontal dummy bases
        def get_native_tip(dummy_arrow, color, pos, angle):
            tip = dummy_arrow.tip.copy()
            tip.set_color(color)
            tip.move_to(ORIGIN)
            tip.shift(ORIGIN - tip.get_right())
            tip.rotate(angle, about_point=ORIGIN)
            tip.shift(pos)
            return tip

        # Generate initial standalone tips
        p1_st1, p1_st2, p1_st3, p1_st4 = get_p1_state(1.0), get_p1_state(2.0), get_p1_state(3.0), get_p1_state(4.0)
        t1_1 = get_native_tip(dummy_a if p1_st1[2] else dummy_b, pink_color, p1_st1[0], p1_st1[1])
        t1_2 = get_native_tip(dummy_a if p1_st2[2] else dummy_b, purple_color, p1_st2[0], p1_st2[1])
        t1_3 = get_native_tip(dummy_a if p1_st3[2] else dummy_b, pink_color, p1_st3[0], p1_st3[1])
        t1_4 = get_native_tip(dummy_a if p1_st4[2] else dummy_b, purple_color, p1_st4[0], p1_st4[1])

        p2_st1, p2_st2, p2_st3, p2_st4 = get_p2_state(1.0), get_p2_state(2.0), get_p2_state(3.0), get_p2_state(4.0)
        t2_1 = get_native_tip(dummy_a if p2_st1[2] else dummy_b, purple_color, p2_st1[0], p2_st1[1])
        t2_2 = get_native_tip(dummy_a if p2_st2[2] else dummy_b, pink_color, p2_st2[0], p2_st2[1])
        t2_3 = get_native_tip(dummy_a if p2_st3[2] else dummy_b, purple_color, p2_st3[0], p2_st3[1])
        t2_4 = get_native_tip(dummy_a if p2_st4[2] else dummy_b, pink_color, p2_st4[0], p2_st4[1])

        tips = VGroup(t1_1, t1_2, t1_3, t1_4, t2_1, t2_2, t2_3, t2_4)

        # Seamlessly swap unified Arrows for discrete Lines and Tips
        self.add(fixed_lines, tips)
        self.remove(vec_a, vec_b, pink_edge, purple_edge, vec_b2, vec_a2, vec_top2, vec_left2)

        circ_tracker = ValueTracker(0)

        def make_updater_p1(tip_mob, base_u, color):
            def updater(m):
                st = get_p1_state(base_u + circ_tracker.get_value())
                m.become(get_native_tip(dummy_a if st[2] else dummy_b, color, st[0], st[1]))
            tip_mob.add_updater(updater)

        def make_updater_p2(tip_mob, base_u, color):
            def updater(m):
                st = get_p2_state(base_u + circ_tracker.get_value())
                m.become(get_native_tip(dummy_a if st[2] else dummy_b, color, st[0], st[1]))
            tip_mob.add_updater(updater)

        make_updater_p1(t1_1, 1.0, pink_color)
        make_updater_p1(t1_2, 2.0, purple_color)
        make_updater_p1(t1_3, 3.0, pink_color)
        make_updater_p1(t1_4, 4.0, purple_color)

        make_updater_p2(t2_1, 1.0, purple_color)
        make_updater_p2(t2_2, 2.0, pink_color)
        make_updater_p2(t2_3, 3.0, purple_color)
        make_updater_p2(t2_4, 4.0, pink_color)

        # Subtle, smooth windback and immediate fluid circulation forward
        self.play(
            circ_tracker.animate.set_value(-0.06),
            run_time=0.4,
            rate_func=linear
        )
        self.play(
            circ_tracker.animate.set_value(2.0),
            run_time=2.8,
            rate_func=smooth
        )

        for tip in tips:
            tip.clear_updaters()

        # ----------------------------------------------------
        # t = 54.00s (05:04:10): Fade in static yellow lines
        # ----------------------------------------------------
        self.wait(1.0) 
        
        SAT_YELLOW = "#FFD700" 
        
        # Centralized and elevated positioning 
        l_start = np.array([-2.4, -2.4, 0])
        l_end = l_start + np.array([2.0, 0.7, 0]) 
        r_start = np.array([0.4, -2.4, 0])
        r_end = r_start + np.array([2.0, 0.7, 0])

        # Left arrow points DOWN (from l_end to l_start) -> -v
        left_arrow = Arrow(l_end, l_start, buff=0, color=SAT_YELLOW, stroke_width=6, max_tip_length_to_length_ratio=0.12)
        # Right arrow points UP (from r_start to r_end) -> v
        right_arrow = Arrow(r_start, r_end, buff=0, color=SAT_YELLOW, stroke_width=6, max_tip_length_to_length_ratio=0.12)
        
        left_tip = left_arrow.tip
        right_tip = right_arrow.tip
        
        left_arrow.remove(left_tip)
        right_arrow.remove(right_tip)
        
        self.play(
            FadeIn(left_arrow),
            FadeIn(right_arrow),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 56.03s (05:06:13): Add independent arrowheads and labels
        # ----------------------------------------------------
        self.wait(1.03)

        label_neg_v = MathTex(r"-\vec{v}", color=SAT_YELLOW).scale(1.1).next_to(l_start, DOWN, buff=0.15)
        label_v = MathTex(r"\vec{v}", color=SAT_YELLOW).scale(1.1).next_to(r_end, UP, buff=0.15)
        
        self.play(
            FadeIn(left_tip),
            FadeIn(right_tip),
            FadeIn(label_neg_v),
            FadeIn(label_v),
            run_time=0.8
        )

        # ----------------------------------------------------
        # t = 58.03s (05:08:13): Add parallelogram top labels centered over top edges
        # ----------------------------------------------------
        self.wait(1.2)

        top_edge_L = Line(p2_top_left, p2_top_right)
        top_edge_R = Line(vec_a_end, top_right_corner)

        label_para_L = MathTex(r"-", r"\vec{a}", r"\wedge", r"\vec{b}").scale(1.1)
        label_para_L[1].set_color(pink_color)
        label_para_L[3].set_color(purple_color)
        label_para_L.next_to(top_edge_L, UP, buff=0.25)

        label_para_R = MathTex(r"\vec{a}", r"\wedge", r"\vec{b}").scale(1.1)
        label_para_R[0].set_color(pink_color)
        label_para_R[2].set_color(purple_color)
        label_para_R.next_to(top_edge_R, UP, buff=0.25)

        label_para_L.set_y(label_para_R.get_y())

        self.play(
            FadeIn(label_para_L),
            FadeIn(label_para_R),
            run_time=0.8
        )

        # Tail buffer
        self.wait(10.00)
        
        
class BivectorTest(Scene):
    def construct(self):
        custom_template = TexTemplate()
        
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}") 
        custom_template.add_to_preamble(r"\usepackage{accents}")
        
        # Reduced horizontal scale to 0.7 and vertical scale to 0.3
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        bivector_text = MathTex(
            r"\bivec{A} \quad \vec{A} \quad \bivec{B} \quad \vec{B}", 
            tex_template=custom_template,
            font_size=96
        )

        self.play(Write(bivector_text))
        self.wait(2)
        


class Scene10(Scene):
    def construct(self):
        # Setup custom TexTemplate for \bivec diacritic
        custom_template = TexTemplate()
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}")
        custom_template.add_to_preamble(r"\usepackage{accents}")
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        pink_color = "#FF66B2"
        purple_color = "#A468FF"
        cyan_color = "#00FFFF"
        SAT_YELLOW = "#FFD700"

        # ----------------------------------------------------
        # Recreate Final Frame of Scene 9 Exactly
        # ----------------------------------------------------
        a_wedge_b = MathTex(r"\vec{a} \wedge \vec{b}").scale(1.1).move_to(UP * 2.8 + LEFT * 5.0)

        # Right Parallelogram (P1)
        diagram_start = np.array([0.5, -0.2, 0])
        vec_b_end = diagram_start + RIGHT * 2.7
        vec_a_end = diagram_start + RIGHT * 1.4 + UP * 1.9
        top_right_corner = vec_a_end + (vec_b_end - diagram_start)

        C0, C1, C2, C3 = diagram_start, vec_a_end, top_right_corner, vec_b_end

        parallelogram = Polygon(
            C0, C1, C2, C3,
            fill_color=ORANGE,
            fill_opacity=0.18,
            stroke_width=0
        )

        l_p1_a = Line(C0, C1, color=pink_color, stroke_width=6)
        l_p1_b = Line(C1, C2, color=purple_color, stroke_width=6)
        l_p1_r = Line(C2, C3, color=pink_color, stroke_width=6)
        l_p1_d = Line(C3, C0, color=purple_color, stroke_width=6)

        fixed_lines_1 = VGroup(l_p1_a, l_p1_b, l_p1_r, l_p1_d)

        # Left Parallelogram (P2)
        p2_start = np.array([-4.0, -0.2, 0])
        p2_b_end = p2_start + RIGHT * 2.7
        p2_top_right = p2_b_end + RIGHT * 1.4 + UP * 1.9
        p2_top_left = p2_start + RIGHT * 1.4 + UP * 1.9

        D0, D1, D2, D3 = p2_start, p2_b_end, p2_top_right, p2_top_left

        parallelogram2 = Polygon(
            D0, D3, D2, D1,
            fill_color=ORANGE,
            fill_opacity=0.18,
            stroke_width=0
        )

        l_p2_b = Line(D0, D1, color=purple_color, stroke_width=6)
        l_p2_a = Line(D1, D2, color=pink_color, stroke_width=6)
        l_p2_t = Line(D2, D3, color=purple_color, stroke_width=6)
        l_p2_l = Line(D3, D0, color=pink_color, stroke_width=6)

        fixed_lines_2 = VGroup(l_p2_b, l_p2_a, l_p2_t, l_p2_l)

        len_a = np.linalg.norm(C1 - C0)
        len_b = np.linalg.norm(C3 - C0)
        dummy_a = Arrow(ORIGIN, RIGHT * len_a, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.08)
        dummy_b = Arrow(ORIGIN, RIGHT * len_b, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.07)

        def get_native_tip(dummy_arrow, color, pos, angle):
            tip = dummy_arrow.tip.copy()
            tip.set_color(color)
            tip.move_to(ORIGIN)
            tip.shift(ORIGIN - tip.get_right())
            tip.rotate(angle, about_point=ORIGIN)
            tip.shift(pos)
            return tip

        t1_1 = get_native_tip(dummy_a, pink_color, C3, Line(C2, C3).get_angle())
        t1_2 = get_native_tip(dummy_b, purple_color, C0, Line(C3, C0).get_angle())
        t1_3 = get_native_tip(dummy_a, pink_color, C1, Line(C0, C1).get_angle())
        t1_4 = get_native_tip(dummy_b, purple_color, C2, Line(C1, C2).get_angle())

        t2_1 = get_native_tip(dummy_b, purple_color, D3, Line(D2, D3).get_angle())
        t2_2 = get_native_tip(dummy_a, pink_color, D0, Line(D3, D0).get_angle())
        t2_3 = get_native_tip(dummy_b, purple_color, D1, Line(D0, D1).get_angle())
        t2_4 = get_native_tip(dummy_a, pink_color, D2, Line(D1, D2).get_angle())

        tips_p1 = VGroup(t1_1, t1_2, t1_3, t1_4)
        tips_p2 = VGroup(t2_1, t2_2, t2_3, t2_4)

        para_text = MathTex(r"ab \sin \theta", color=BLUE).scale(0.9).move_to(parallelogram.get_center())

        top_edge_L = Line(D3, D2)
        top_edge_R = Line(C1, C2)

        label_para_L = MathTex(r"-", r"\vec{a}", r"\wedge", r"\vec{b}").scale(1.1)
        label_para_L[1].set_color(pink_color)
        label_para_L[3].set_color(purple_color)
        label_para_L.next_to(top_edge_L, UP, buff=0.25)

        label_para_R = MathTex(r"\vec{a}", r"\wedge", r"\vec{b}").scale(1.1)
        label_para_R[0].set_color(pink_color)
        label_para_R[2].set_color(purple_color)
        label_para_R.next_to(top_edge_R, UP, buff=0.25)
        label_para_L.set_y(label_para_R.get_y())

        l_start = np.array([-2.4, -2.4, 0])
        l_end = l_start + np.array([2.0, 0.7, 0])
        r_start = np.array([0.4, -2.4, 0])
        r_end = r_start + np.array([2.0, 0.7, 0])

        left_arrow = Arrow(l_end, l_start, buff=0, color=SAT_YELLOW, stroke_width=6, max_tip_length_to_length_ratio=0.12)
        right_arrow = Arrow(r_start, r_end, buff=0, color=SAT_YELLOW, stroke_width=6, max_tip_length_to_length_ratio=0.12)
        left_tip = left_arrow.tip
        right_tip = right_arrow.tip
        left_arrow.remove(left_tip)
        right_arrow.remove(right_tip)

        label_neg_v = MathTex(r"-\vec{v}", color=SAT_YELLOW).scale(1.1).next_to(l_start, DOWN, buff=0.15)
        label_v = MathTex(r"\vec{v}", color=SAT_YELLOW).scale(1.1).next_to(r_end, UP, buff=0.15)

        vec_b_dummy = Arrow(diagram_start, vec_b_end, buff=0)
        vec_a_dummy = Arrow(diagram_start, vec_a_end, buff=0)
        angle = Angle(vec_b_dummy, vec_a_dummy, radius=0.6, color=cyan_color, stroke_width=4)
        theta = MathTex(r"\theta", color=cyan_color).scale(0.95).move_to(diagram_start + RIGHT * 0.85 + UP * 0.28)
        
        label_a = MathTex(r"\vec{a}", color=pink_color).scale(1.1).next_to(vec_a_end, UP, buff=0.15)
        label_b = MathTex(r"\vec{b}", color=purple_color).scale(1.1).next_to(vec_b_end, DOWN, buff=0.15)
        label_b.shift(vec_a_end - diagram_start) 
        
        label_b2 = MathTex(r"\vec{b}", color=purple_color).scale(1.1).next_to(p2_b_end, DOWN, buff=0.15)
        label_a2 = MathTex(r"\vec{a}", color=pink_color).scale(1.1).next_to(p2_top_right, RIGHT, buff=0.15)

        self.add(
            a_wedge_b,
            parallelogram, parallelogram2,
            fixed_lines_1, fixed_lines_2,
            tips_p1, tips_p2,
            para_text, label_para_L, label_para_R,
            left_arrow, right_arrow, left_tip, right_tip,
            label_neg_v, label_v,
            label_a, label_b, label_b2, label_a2, angle, theta
        )

        # ----------------------------------------------------
        # t = 0.00s (5:18:10): Start Scene 10
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Rectification into rectangles
        # ----------------------------------------------------
        self.wait(1.96)

        RATIO_V = 0.25 / 1.9    
        RATIO_HL = 0.25 / 2.7   
        RATIO_HR = 0.25 / 1.4   

        RL0 = np.array([-3.35, -0.2, 0])
        RL1 = np.array([-0.65, -0.2, 0])
        RL2 = np.array([-0.65, 1.7, 0])
        RL3 = np.array([-3.35, 1.7, 0])

        rect_poly_L = Polygon(
            RL0, RL1, RL2, RL3,
            fill_color=pink_color,
            fill_opacity=0.18,
            stroke_width=0
        )

        rect_arrow_L_bot = Arrow(RL1, RL0, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HL)
        rect_arrow_L_left = Arrow(RL0, RL3, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        rect_arrow_L_top = Arrow(RL3, RL2, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HL)
        rect_arrow_L_right = Arrow(RL2, RL1, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)

        RR0 = np.array([1.1, -0.2, 0])
        RR1 = np.array([2.5, -0.2, 0])
        RR2 = np.array([2.5, 1.7, 0])
        RR3 = np.array([1.1, 1.7, 0])

        rect_poly_R = Polygon(
            RR0, RR1, RR2, RR3,
            fill_color=purple_color,
            fill_opacity=0.18,
            stroke_width=0
        )

        rect_arrow_R_bot = Arrow(RR1, RR0, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HR)
        rect_arrow_R_left = Arrow(RR0, RR3, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        rect_arrow_R_top = Arrow(RR3, RR2, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HR)
        rect_arrow_R_right = Arrow(RR2, RR1, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)

        bivec_A = MathTex(r"\bivec{A}", color=pink_color, tex_template=custom_template).scale(1.2)
        bivec_A.next_to(Line(RL3, RL2), UP, buff=0.25)

        bivec_B = MathTex(r"\bivec{B}", color=purple_color, tex_template=custom_template).scale(1.2)
        bivec_B.next_to(Line(RR3, RR2), UP, buff=0.25)
        bivec_B.set_y(bivec_A.get_y())

        self.play(
            FadeOut(a_wedge_b),
            FadeOut(left_arrow), FadeOut(right_arrow),
            FadeOut(left_tip), FadeOut(right_tip),
            FadeOut(label_neg_v), FadeOut(label_v),
            FadeOut(para_text),
            FadeOut(label_a), FadeOut(label_b), 
            FadeOut(label_b2), FadeOut(label_a2), 
            FadeOut(angle), FadeOut(theta),

            ReplacementTransform(parallelogram2, rect_poly_L),
            ReplacementTransform(VGroup(l_p2_l, t2_2), rect_arrow_L_left),
            ReplacementTransform(VGroup(l_p2_t, t2_1), rect_arrow_L_top),
            ReplacementTransform(VGroup(l_p2_a, t2_4), rect_arrow_L_right),
            ReplacementTransform(VGroup(l_p2_b, t2_3), rect_arrow_L_bot),
            ReplacementTransform(label_para_L, bivec_A),

            ReplacementTransform(parallelogram, rect_poly_R),
            ReplacementTransform(VGroup(l_p1_a, t1_3), rect_arrow_R_left),
            ReplacementTransform(VGroup(l_p1_b, t1_4), rect_arrow_R_top),
            ReplacementTransform(VGroup(l_p1_r, t1_1), rect_arrow_R_right),
            ReplacementTransform(VGroup(l_p1_d, t1_2), rect_arrow_R_bot),
            ReplacementTransform(label_para_R, bivec_B),

            run_time=1.8
        )

        # ----------------------------------------------------
        # t = 5:24:00: Rectangles move to touch side-by-side
        # ----------------------------------------------------
        self.wait(2.07)

        group_A = VGroup(
            rect_poly_L, rect_arrow_L_bot, rect_arrow_L_right, rect_arrow_L_top, rect_arrow_L_left, bivec_A
        )
        group_B = VGroup(
            rect_poly_R, rect_arrow_R_bot, rect_arrow_R_right, rect_arrow_R_top, rect_arrow_R_left, bivec_B
        )

        self.play(
            group_A.animate.shift(RIGHT * 0.47), 
            group_B.animate.shift(LEFT * 1.22),
            run_time=1.0
        )

        # Pre-fill structure placed before arrows shrink to avoid dark seam
        M_RL0 = np.array([-2.88, -0.2, 0])
        M_RL1 = np.array([-0.15, -0.2, 0])
        M_RL2 = np.array([-0.15, 1.7, 0])
        M_RL3 = np.array([-2.88, 1.7, 0])

        M_RR0 = np.array([-0.15, -0.2, 0])
        M_RR1 = np.array([1.28, -0.2, 0])
        M_RR2 = np.array([1.28, 1.7, 0])
        M_RR3 = np.array([-0.15, 1.7, 0])

        merged_poly_L = Polygon(M_RL0, M_RL1, M_RL2, M_RL3, fill_color=pink_color, fill_opacity=0.18, stroke_width=0)
        merged_poly_R = Polygon(M_RR0, M_RR1, M_RR2, M_RR3, fill_color=purple_color, fill_opacity=0.18, stroke_width=0)

        self.remove(rect_poly_L, rect_poly_R)
        self.add(merged_poly_L, merged_poly_R)

        # ----------------------------------------------------
        # Elastic stretching of opposite sides
        # ----------------------------------------------------
        self.wait(1.29)

        pink_top_start = rect_arrow_L_top.get_start()
        pink_top_end_orig = rect_arrow_L_top.get_end()
        pink_top_end_target = rect_arrow_R_top.get_end()

        purp_bot_start = rect_arrow_R_bot.get_start()
        purp_bot_end_orig = rect_arrow_R_bot.get_end()
        purp_bot_end_target = rect_arrow_L_bot.get_end()

        stretch_tracker = ValueTracker(0)

        def update_pink_top(m):
            v = stretch_tracker.get_value()
            cur_end = interpolate(pink_top_end_orig, pink_top_end_target, v)
            m.put_start_and_end_on(pink_top_start, cur_end)

        def update_purp_bot(m):
            v = stretch_tracker.get_value()
            cur_end = interpolate(purp_bot_end_orig, purp_bot_end_target, v)
            m.put_start_and_end_on(purp_bot_start, cur_end)

        rect_arrow_L_top.add_updater(update_pink_top)
        rect_arrow_R_bot.add_updater(update_purp_bot)

        rect_arrow_L_top.set_z_index(10)
        rect_arrow_R_top.set_z_index(0)
        rect_arrow_R_bot.set_z_index(10)
        rect_arrow_L_bot.set_z_index(0)

        self.play(
            stretch_tracker.animate.set_value(-0.15),
            run_time=0.4,
            rate_func=linear
        )
        
        self.play(
            stretch_tracker.animate.set_value(1.0),
            run_time=1.0,
            rate_func=smooth
        )

        rect_arrow_L_top.clear_updaters()
        rect_arrow_R_bot.clear_updaters()

        # ----------------------------------------------------
        # Shrink touching edges and turn white before fading out
        # ----------------------------------------------------
        self.wait(1.48)

        pink_right_start = rect_arrow_L_right.get_start() 
        pink_right_end_orig = rect_arrow_L_right.get_end() 

        purp_left_start = rect_arrow_R_left.get_start()   
        purp_left_end_orig = rect_arrow_R_left.get_end()   

        shrink_tracker = ValueTracker(0)

        def update_pink_recede(m):
            v = shrink_tracker.get_value()
            cur_end = interpolate(pink_right_end_orig, pink_right_start, v)
            m.put_start_and_end_on(pink_right_start, cur_end)

        def update_purp_recede(m):
            v = shrink_tracker.get_value()
            cur_end = interpolate(purp_left_end_orig, purp_left_start, v)
            m.put_start_and_end_on(purp_left_start, cur_end)

        rect_arrow_L_right.add_updater(update_pink_recede)
        rect_arrow_R_left.add_updater(update_purp_recede)

        self.play(
            shrink_tracker.animate.set_value(0.5),
            run_time=0.8,
            rate_func=smooth
        )

        rect_arrow_L_right.clear_updaters()
        rect_arrow_R_left.clear_updaters()

        self.play(
            rect_arrow_L_right.animate.set_color(WHITE),
            rect_arrow_R_left.animate.set_color(WHITE),
            run_time=0.15
        )
        
        self.play(
            FadeOut(rect_arrow_L_right),
            FadeOut(rect_arrow_R_left),
            run_time=0.25
        )

        # ----------------------------------------------------
        # Rigidly slide existing labels A and B inward to form A + B
        # ----------------------------------------------------
        self.wait(0.2)
        
        plus_sign = MathTex("+").scale(1.2).move_to(np.array([-0.15, bivec_A.get_y(), 0]))

        target_bivec_A_pos = plus_sign.get_center() + LEFT * 0.7
        target_bivec_B_pos = plus_sign.get_center() + RIGHT * 0.7

        self.play(
            bivec_A.animate.move_to(target_bivec_A_pos),
            bivec_B.animate.move_to(target_bivec_B_pos),
            FadeIn(plus_sign),
            run_time=0.8
        )

        # ----------------------------------------------------
        # t = 5:37:18: Smooth Translation Reset to separated A and B
        # ----------------------------------------------------
        self.wait(5.93)

        orig_poly_L = Polygon(RL0, RL1, RL2, RL3, fill_color=pink_color, fill_opacity=0.18, stroke_width=0)
        orig_L_bot = Arrow(RL1, RL0, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HL)
        orig_L_left = Arrow(RL0, RL3, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        orig_L_top = Arrow(RL3, RL2, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HL)
        orig_L_right = Arrow(RL2, RL1, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        
        orig_bivec_A = MathTex(r"\bivec{A}", color=pink_color, tex_template=custom_template).scale(1.2).next_to(Line(RL3, RL2), UP, buff=0.25)
        
        orig_poly_R = Polygon(RR0, RR1, RR2, RR3, fill_color=purple_color, fill_opacity=0.18, stroke_width=0)
        orig_R_bot = Arrow(RR1, RR0, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HR)
        orig_R_left = Arrow(RR0, RR3, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        orig_R_top = Arrow(RR3, RR2, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HR)
        orig_R_right = Arrow(RR2, RR1, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        
        orig_bivec_B = MathTex(r"\bivec{B}", color=purple_color, tex_template=custom_template).scale(1.2).next_to(Line(RR3, RR2), UP, buff=0.25)
        orig_bivec_B.set_y(orig_bivec_A.get_y())

        # Inject hidden inner borders at the visible merged seam
        new_L_right = Arrow(np.array([-0.15, 1.7, 0]), np.array([-0.15, -0.2, 0]), buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V).set_opacity(0)
        new_R_left = Arrow(np.array([-0.15, -0.2, 0]), np.array([-0.15, 1.7, 0]), buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V).set_opacity(0)
        self.add(new_L_right, new_R_left)

        self.play(
            ReplacementTransform(merged_poly_L, orig_poly_L),
            ReplacementTransform(rect_arrow_L_bot, orig_L_bot),
            ReplacementTransform(rect_arrow_L_left, orig_L_left),
            ReplacementTransform(rect_arrow_L_top, orig_L_top),
            Transform(new_L_right, orig_L_right), 
            bivec_A.animate.move_to(orig_bivec_A.get_center()),
            
            ReplacementTransform(merged_poly_R, orig_poly_R),
            ReplacementTransform(rect_arrow_R_top, orig_R_top),
            ReplacementTransform(rect_arrow_R_right, orig_R_right),
            ReplacementTransform(rect_arrow_R_bot, orig_R_bot),
            Transform(new_R_left, orig_R_left),
            bivec_B.animate.move_to(orig_bivec_B.get_center()),
            
            FadeOut(plus_sign),
            run_time=1.2
        )
        self.remove(new_L_right, new_R_left)
        self.add(orig_L_right, orig_R_left)

        # ----------------------------------------------------
        # t = 5:39:03: Invert B - Label becomes -B and Circulation Inverts CCW
        # ----------------------------------------------------
        self.wait(0.55) 

        # Setup CCW arrows for B mapped natively to RR boundaries
        ccw_R_bot = Arrow(RR0, RR1, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HR)
        ccw_R_right = Arrow(RR1, RR2, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        ccw_R_top = Arrow(RR2, RR3, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HR)
        ccw_R_left = Arrow(RR3, RR0, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)

        label_neg_B = MathTex(r"-\bivec{B}", color=purple_color, tex_template=custom_template).scale(1.2).move_to(orig_bivec_B.get_center())

        self.play(
            ReplacementTransform(orig_R_bot, ccw_R_bot),
            ReplacementTransform(orig_R_right, ccw_R_right),
            ReplacementTransform(orig_R_top, ccw_R_top),
            ReplacementTransform(orig_R_left, ccw_R_left),
            ReplacementTransform(bivec_B, label_neg_B),
            run_time=1.50 
        )

        group_B_final = VGroup(orig_poly_R, ccw_R_bot, ccw_R_right, ccw_R_top, ccw_R_left, label_neg_B)

        # ----------------------------------------------------
        # t = 5:42:05: -B slides left so its left edge touches A's right edge
        # ----------------------------------------------------
        self.wait(1.00)

        # Shift bounds precisely by 1.69 to sit perfectly side-by-side with 0.06 gap 
        self.play(
            group_B_final.animate.shift(LEFT * 1.69),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 5:45:01: -B slides further left so its right edge sits inside A's right edge
        # ----------------------------------------------------
        self.wait(1.93)

        self.play(
            group_B_final.animate.shift(LEFT * 1.52),
            bivec_A.animate.shift(LEFT * 0.7),
            run_time=1.2
        )

        # ----------------------------------------------------
        # t = 5:49:07: Sequence of Vector Cancellations (Shrinking Edges)
        # ----------------------------------------------------
        self.wait(3.10)

        # 1. Right Edge Vectors Shrink to Center, Flash White, Fade Out
        v_right = ValueTracker(0)
        orig_pink_R_tip = orig_L_right.get_end()
        orig_purp_R_tip = ccw_R_right.get_end()
        center_R = (orig_pink_R_tip + orig_purp_R_tip) / 2

        # Min threshold guarantees length is slightly > 0 protecting from spin/jolts
        def update_pink_R(m):
            v = min(v_right.get_value(), 0.98)
            cur_end = interpolate(orig_pink_R_tip, center_R, v)
            m.put_start_and_end_on(orig_L_right.get_start(), cur_end)

        def update_purp_R(m):
            v = min(v_right.get_value(), 0.98)
            cur_end = interpolate(orig_purp_R_tip, center_R, v)
            m.put_start_and_end_on(ccw_R_right.get_start(), cur_end)

        orig_L_right.add_updater(update_pink_R)
        ccw_R_right.add_updater(update_purp_R)

        self.play(v_right.animate.set_value(1.0), run_time=0.8, rate_func=smooth)
        orig_L_right.clear_updaters()
        ccw_R_right.clear_updaters()

        self.play(orig_L_right.animate.set_color(WHITE), ccw_R_right.animate.set_color(WHITE), run_time=0.15)
        self.play(FadeOut(orig_L_right), FadeOut(ccw_R_right), run_time=0.25)

        # Attach updaters to Polygons so fills shrink continuously during x-axis collapses
        def update_pink_poly(m):
            m.become(Polygon(
                np.array([-3.35, -0.2, 0]),
                orig_L_bot.get_start(),
                orig_L_top.get_end(),
                np.array([-3.35, 1.7, 0]),
                fill_color=pink_color, fill_opacity=0.18, stroke_width=0
            ))

        def update_purp_poly(m):
            m.become(Polygon(
                np.array([-2.11, -0.2, 0]),
                ccw_R_bot.get_end(),
                ccw_R_top.get_start(),
                np.array([-2.11, 1.7, 0]),
                fill_color=purple_color, fill_opacity=0.18, stroke_width=0
            ))

        orig_poly_L.add_updater(update_pink_poly)
        orig_poly_R.add_updater(update_purp_poly)

        # 2. Top Edge Vectors Shrink Leftward
        self.bring_to_front(orig_L_top)
        
        v_top = ValueTracker(0)
        orig_pink_T_tip = orig_L_top.get_end()
        orig_purp_T_base = ccw_R_top.get_start()

        def update_pink_T(m):
            v = v_top.get_value()
            cur_end = interpolate(orig_pink_T_tip, np.array([-2.11, 1.7, 0]), v)
            m.put_start_and_end_on(orig_L_top.get_start(), cur_end)

        def update_purp_T(m):
            v = min(v_top.get_value(), 0.99)
            cur_start = interpolate(orig_purp_T_base, np.array([-2.11, 1.7, 0]), v)
            m.put_start_and_end_on(cur_start, ccw_R_top.get_end())

        orig_L_top.add_updater(update_pink_T)
        ccw_R_top.add_updater(update_purp_T)

        self.play(v_top.animate.set_value(1.0), run_time=1.2, rate_func=smooth)
        orig_L_top.clear_updaters()
        ccw_R_top.clear_updaters()

        self.play(ccw_R_top.animate.set_color(WHITE), run_time=0.15)
        self.play(FadeOut(ccw_R_top), run_time=0.25)

        # 3. Bottom Edge Vectors Shrink Leftward
        self.bring_to_front(orig_L_bot)
        
        v_bot = ValueTracker(0)
        orig_purp_B_tip = ccw_R_bot.get_end()
        orig_pink_B_base = orig_L_bot.get_start()

        def update_purp_B(m):
            v = min(v_bot.get_value(), 0.99)
            cur_end = interpolate(orig_purp_B_tip, np.array([-2.11, -0.2, 0]), v)
            m.put_start_and_end_on(ccw_R_bot.get_start(), cur_end)

        def update_pink_B(m):
            v = v_bot.get_value()
            cur_start = interpolate(orig_pink_B_base, np.array([-2.11, -0.2, 0]), v)
            m.put_start_and_end_on(cur_start, orig_L_bot.get_end())

        ccw_R_bot.add_updater(update_purp_B)
        orig_L_bot.add_updater(update_pink_B)

        self.play(v_bot.animate.set_value(1.0), run_time=1.2, rate_func=smooth)
        ccw_R_bot.clear_updaters()
        orig_L_bot.clear_updaters()

        self.play(ccw_R_bot.animate.set_color(WHITE), run_time=0.15)
        self.play(FadeOut(ccw_R_bot), run_time=0.25)

        orig_poly_L.clear_updaters()
        orig_poly_R.clear_updaters()

        # Dummy group correctly structures strict rigid alignment coordinates
        dummy_group = VGroup(
            MathTex(r"\bivec{A}", color=pink_color, tex_template=custom_template).scale(1.2),
            MathTex(r"-\bivec{B}", color=purple_color, tex_template=custom_template).scale(1.2)
        ).arrange(RIGHT, buff=0.15).move_to(np.array([-2.70, bivec_A.get_y(), 0]))

        self.play(
            bivec_A.animate.move_to(dummy_group[0].get_center()),
            label_neg_B.animate.move_to(dummy_group[1].get_center()),
            FadeOut(orig_poly_R),
            run_time=1.0
        )

        # Tail buffer
        self.wait(10.00)



class CameraFacingArrow(VGroup):
    def __init__(self, start, end, color, tip_length, camera_dir, **kwargs):
        super().__init__(**kwargs)
        self.start_pt = np.array(start, dtype=float)
        self.end_pt = np.array(end, dtype=float)
        self.color = color
        self.tip_length = tip_length
        self.camera_dir = np.array(camera_dir, dtype=float)
        
        # Initialize with dummy distinct points so Line doesn't collapse to 1D on init
        self.line = Line(LEFT, RIGHT, color=self.color, stroke_width=6, buff=0)
        self.tip = Polygon(ORIGIN, RIGHT, UP, fill_color=self.color, fill_opacity=1, stroke_width=0)
        
        self.add(self.line, self.tip)
        self.update_geometry()
        
    def set_start_and_end(self, start, end):
        self.start_pt = np.array(start, dtype=float)
        self.end_pt = np.array(end, dtype=float)
        self.update_geometry()
        
    def update_geometry(self):
        d = self.end_pt - self.start_pt
        length = np.linalg.norm(d)
        
        # The critical fix: Intercept 0-length lines to prevent ThreeDCamera IndexError
        if length < 1e-4:
            d = np.array([1e-4, 0, 0])
            length = 1e-4
            self.tip.set_opacity(0)
            self.line.set_opacity(0)
        else:
            self.tip.set_opacity(1)
            self.line.set_opacity(1)
            
        d = d / length
        
        # Dynamic tip sizing prevents jitter/overshoot as length approaches 0
        actual_tip_length = min(self.tip_length, length)
        actual_tip_width = actual_tip_length * 0.8
        
        c = self.camera_dir
        c_len = np.linalg.norm(c)
        if c_len > 1e-4:
            c = c / c_len
        else:
            c = OUT
            
        n = c - np.dot(c, d) * d
        n_len = np.linalg.norm(n)
        if n_len > 1e-4:
            n = n / n_len
        else:
            fallback = OUT if abs(d[2]) < 0.9 else RIGHT
            n = fallback - np.dot(fallback, d) * d
            n = n / np.linalg.norm(n)
            
        r = np.cross(n, d)
        
        safe_end_pt = self.start_pt + d * length
        line_end = safe_end_pt - actual_tip_length * d
        
        # Ensure the physical Line object never drops to exactly 0 length
        if np.linalg.norm(line_end - self.start_pt) < 1e-4:
            line_end = self.start_pt + d * 1e-4
            
        self.line.put_start_and_end_on(self.start_pt, line_end)
        
        p0 = safe_end_pt
        p1 = safe_end_pt - actual_tip_length * d + (actual_tip_width / 2) * r
        p2 = safe_end_pt - actual_tip_length * d - (actual_tip_width / 2) * r
        
        current_opacity = self.tip.get_fill_opacity()
        self.tip.become(Polygon(p0, p1, p2, fill_color=self.color, fill_opacity=current_opacity, stroke_width=0))


class Scene11(ThreeDScene):
    def construct(self):
        custom_template = TexTemplate()
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}")
        custom_template.add_to_preamble(r"\usepackage{accents}")
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        pink_color = "#FF66B2"     
        purple_color = "#A468FF"   
        SAT_YELLOW = "#FFD700"
        
        cam_dir_3d = np.array([0, -np.sin(65 * DEGREES), np.cos(65 * DEGREES)])

        # ----------------------------------------------------
        # Scene 10 Final Frame - Flawless Math Match
        # ----------------------------------------------------
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)

        RATIO_V = 0.25 / 1.9    
        RATIO_HL = 0.25 / 2.7

        # 1. Left arrow (orig_L_left) - Pink UP
        RL0 = np.array([-3.35, -0.2, 0])
        RL3 = np.array([-3.35, 1.7, 0])
        start_arr_l = Arrow(RL0, RL3, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        
        # 2. Top arrow (orig_L_top) - Pink RIGHT
        # Initialized at original Scene 10 length, then updated to create the exact tip distortion 
        RL2 = np.array([-0.65, 1.7, 0])
        start_arr_t = Arrow(RL3, RL2, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HL)
        start_arr_t.put_start_and_end_on(RL3, np.array([-2.11, 1.7, 0]))

        # 3. Right arrow (ccw_R_left) - Purple DOWN
        # Initialized at original position, then identically shifted
        RR3 = np.array([1.1, 1.7, 0])
        RR0 = np.array([1.1, -0.2, 0])
        start_arr_r = Arrow(RR3, RR0, buff=0, color=purple_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_V)
        start_arr_r.shift(LEFT * 3.21)

        # 4. Bottom arrow (orig_L_bot) - Pink LEFT
        RL1 = np.array([-0.65, -0.2, 0])
        start_arr_b = Arrow(RL1, RL0, buff=0, color=pink_color, stroke_width=6, max_tip_length_to_length_ratio=RATIO_HL)
        start_arr_b.put_start_and_end_on(np.array([-2.11, -0.2, 0]), RL0)
        
        # 5. Polygon (orig_poly_L) - Pink Fill
        start_poly = Polygon(
            np.array([-3.35, -0.2, 0]),
            np.array([-2.11, -0.2, 0]),
            np.array([-2.11, 1.7, 0]),
            np.array([-3.35, 1.7, 0]),
            fill_color=pink_color, fill_opacity=0.18, stroke_width=0
        )
        
        start_group = VGroup(start_poly, start_arr_l, start_arr_t, start_arr_r, start_arr_b)
        
        # 6. Labels calculated identically to Scene 10 layout bounds
        dummy_A = MathTex(r"\bivec{A}", color=pink_color, tex_template=custom_template).scale(1.2)
        dummy_A.next_to(Line(RL3, RL2), UP, buff=0.25)
        
        label_ab = VGroup(
            MathTex(r"\bivec{A}", color=pink_color, tex_template=custom_template).scale(1.2),
            MathTex(r"-\bivec{B}", color=purple_color, tex_template=custom_template).scale(1.2)
        ).arrange(RIGHT, buff=0.15).move_to(np.array([-2.70, dummy_A.get_y(), 0]))

        self.add(start_group, label_ab)

        # ----------------------------------------------------
        # t = 0.00s (5:58:06): Start Scene 11
        # ----------------------------------------------------
        
        # ----------------------------------------------------
        # t = 2.27s (6:00:22): Reset into A and B angled in 3D
        # ----------------------------------------------------
        self.wait(2.27)

        def create_rect_bivector(center_pos, vec_lr, vec_bt, color, label_tex, label_dir, is_cw=True):
            w = np.linalg.norm(vec_lr)
            h = np.linalg.norm(vec_bt)
            
            c0 = np.array([-w/2, -h/2, 0])
            c1 = np.array([w/2, -h/2, 0])
            c2 = np.array([w/2, h/2, 0])
            c3 = np.array([-w/2, h/2, 0])
            
            target_x = vec_lr / w
            target_y = vec_bt / h
            target_z = np.cross(target_x, target_y)
            matrix = np.column_stack((target_x, target_y, target_z))
            
            def map_pt(pt):
                return np.dot(matrix, pt) + center_pos
            
            p0, p1, p2, p3 = map_pt(c0), map_pt(c1), map_pt(c2), map_pt(c3)
            
            poly = Polygon(p0, p1, p2, p3, fill_color=color, fill_opacity=0.18, stroke_width=0)
            
            if is_cw:
                arr_l = CameraFacingArrow(p0, p3, color, 0.25, cam_dir_3d) 
                arr_t = CameraFacingArrow(p3, p2, color, 0.25, cam_dir_3d) 
                arr_r = CameraFacingArrow(p2, p1, color, 0.25, cam_dir_3d) 
                arr_b = CameraFacingArrow(p1, p0, color, 0.25, cam_dir_3d) 
            else:
                arr_l = CameraFacingArrow(p3, p0, color, 0.25, cam_dir_3d) 
                arr_t = CameraFacingArrow(p2, p3, color, 0.25, cam_dir_3d) 
                arr_r = CameraFacingArrow(p1, p2, color, 0.25, cam_dir_3d) 
                arr_b = CameraFacingArrow(p0, p1, color, 0.25, cam_dir_3d) 
                
            label = MathTex(label_tex, color=color, tex_template=custom_template).scale(1.2)
            
            if np.array_equal(label_dir, UP + LEFT):
                label_pos = p3 + target_x * (-0.35) + target_y * (0.45)
            elif np.array_equal(label_dir, UP + RIGHT):
                label_pos = p2 + target_x * (0.35) + target_y * (0.45)
            else:
                label_pos = center_pos
                
            label.apply_matrix(matrix)
            label.move_to(label_pos)
            
            group = VGroup(poly, arr_l, arr_t, arr_r, arr_b, label)
            return group

        # Bivector A (Pink, CW)
        group_A_3d = create_rect_bivector(
            center_pos=np.array([-2.35, 0.75, 0]), 
            vec_lr=np.array([2.7, 1.5, 0]), 
            vec_bt=np.array([0, 0, 1.9]), 
            color=pink_color, 
            label_tex=r"\bivec{A}", 
            label_dir=UP + LEFT,
            is_cw=True
        )
        
        # Bivector B (Purple, CW)
        group_B_3d = create_rect_bivector(
            center_pos=np.array([2.35, 0.75, 0]), 
            vec_lr=np.array([2.7, -1.5, 0]), 
            vec_bt=np.array([0, 0, 1.9]), 
            color=purple_color, 
            label_tex=r"\bivec{B}", 
            label_dir=UP + RIGHT,
            is_cw=True
        )
        
        self.move_camera(
            phi=65 * DEGREES, 
            theta=-90 * DEGREES,
            added_anims=[
                ReplacementTransform(start_poly, group_A_3d[0]),
                ReplacementTransform(start_arr_l, group_A_3d[1]), 
                ReplacementTransform(start_arr_t, group_A_3d[2]), 
                ReplacementTransform(start_arr_b, group_A_3d[4]), 
                ReplacementTransform(start_arr_r, group_B_3d[3]), 
                ReplacementTransform(label_ab[0], group_A_3d[5]),
                ReplacementTransform(label_ab[1], group_B_3d[5]), 
                FadeIn(group_A_3d[3]), 
                FadeIn(group_B_3d[0]), 
                FadeIn(group_B_3d[1]), 
                FadeIn(group_B_3d[2]), 
                FadeIn(group_B_3d[4])
            ],
            run_time=1.5
        )
        
        # ----------------------------------------------------
        # t = 6:05:01: A and B slide together
        # ----------------------------------------------------
        self.wait(3.15)
        
        self.play(
            group_A_3d.animate.shift(RIGHT * 1.0),
            group_B_3d.animate.shift(LEFT * 1.0),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 6:07:00: Touching edges shrink and cancel
        # ----------------------------------------------------
        self.wait(0.98)

        A_verts = group_A_3d[0].get_vertices()
        B_verts = group_B_3d[0].get_vertices()
        
        orig_A_r_start = A_verts[2]
        orig_A_r_end = A_verts[1]
        orig_B_l_start = B_verts[0]
        orig_B_l_end = B_verts[3]
        
        center_A = (orig_A_r_start + orig_A_r_end) / 2
        center_B = (orig_B_l_start + orig_B_l_end) / 2
        
        touching_edges = VGroup(group_A_3d[3], group_B_3d[1])
        
        def shrink_edges(m, alpha):
            v = min(alpha, 0.95)
            
            cur_start_A = orig_A_r_start + v * (center_A - orig_A_r_start)
            cur_end_A = orig_A_r_end + v * (center_A - orig_A_r_end)
            m[0].set_start_and_end(cur_start_A, cur_end_A)
            
            cur_start_B = orig_B_l_start + v * (center_B - orig_B_l_start)
            cur_end_B = orig_B_l_end + v * (center_B - orig_B_l_end)
            m[1].set_start_and_end(cur_start_B, cur_end_B)
            
        self.play(
            UpdateFromAlphaFunc(touching_edges, shrink_edges),
            run_time=0.8
        )
        
        self.play(
            group_A_3d[3].animate.set_color(WHITE), 
            group_B_3d[1].animate.set_color(WHITE), 
            run_time=0.15
        )
        
        self.play(
            FadeOut(group_A_3d[3]), 
            FadeOut(group_B_3d[1]), 
            run_time=0.25
        )

        # ----------------------------------------------------
        # t = 6:09:13: Yellow arrows grow and C face fills
        # ----------------------------------------------------
        self.wait(1.01)

        A_BL = A_verts[0]
        A_TL = A_verts[3]
        B_BR = B_verts[1]
        B_TR = B_verts[2]

        top_yellow_arrow = CameraFacingArrow(A_TL, A_TL, SAT_YELLOW, 0.25, cam_dir_3d)
        self.add(top_yellow_arrow)
        
        def grow_top(m, alpha):
            cur_end = A_TL + alpha * (B_TR - A_TL)
            m.set_start_and_end(A_TL, cur_end)
            
        self.play(
            UpdateFromAlphaFunc(top_yellow_arrow, grow_top),
            FadeOut(group_A_3d[2]), 
            FadeOut(group_B_3d[2]),
            run_time=0.8
        )
        
        bot_yellow_arrow = CameraFacingArrow(B_BR, B_BR, SAT_YELLOW, 0.25, cam_dir_3d)
        self.add(bot_yellow_arrow)
        
        def grow_bot(m, alpha):
            cur_end = B_BR + alpha * (A_BL - B_BR)
            m.set_start_and_end(B_BR, cur_end)
            
        self.play(
            UpdateFromAlphaFunc(bot_yellow_arrow, grow_bot),
            FadeOut(group_A_3d[4]), 
            FadeOut(group_B_3d[4]),
            run_time=0.8
        )
        
        yellow_poly = Polygon(A_BL, B_BR, B_TR, A_TL, fill_color=SAT_YELLOW, fill_opacity=0.18, stroke_width=0)
        
        w_C = np.linalg.norm(B_BR - A_BL)
        h_C = np.linalg.norm(A_TL - A_BL)
        
        target_x_C = (B_BR - A_BL) / w_C
        target_y_C = (A_TL - A_BL) / h_C
        target_z_C = np.cross(target_x_C, target_y_C)
        matrix_C = np.column_stack((target_x_C, target_y_C, target_z_C))
        
        label_C = MathTex(r"\bivec{A} + \bivec{B}", color=SAT_YELLOW, tex_template=custom_template).scale(1.2)
        
        center_bot = (A_BL + B_BR) / 2
        label_pos = center_bot + target_y_C * (-0.45)
        
        label_C.apply_matrix(matrix_C)
        label_C.move_to(label_pos)

        self.play(
            FadeIn(yellow_poly),
            FadeIn(label_C),
            run_time=1.0
        )
        
        self.wait(10.0)
        


class Scene12(ThreeDScene):
    def construct(self):
        custom_template = TexTemplate()
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}")
        custom_template.add_to_preamble(r"\usepackage{accents}")
        custom_template.add_to_preamble(r"\usepackage{cjhebrew}")
        custom_template.add_to_preamble(r"\newcommand{\tav}{\text{\cjhebrew{t}}}")
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        pink_color = "#FF66B2"     
        purple_color = "#A468FF"   
        SAT_YELLOW = "#FFD700"
        SCALE_FACTOR = 0.85
        
        cam_dir_3d = np.array([0, -np.sin(65 * DEGREES), np.cos(65 * DEGREES)])

        # ----------------------------------------------------
        # t = 0.00s (6:21:22): Start Scene 12
        # ----------------------------------------------------
        self.set_camera_orientation(phi=65 * DEGREES, theta=-90 * DEGREES)

        center_A = np.array([-1.35, 0.75, 0])
        vec_lr_A = np.array([2.7, 1.5, 0])
        vec_bt_A = np.array([0, 0, 1.9])
        
        p0_A = center_A - vec_lr_A/2 - vec_bt_A/2
        p1_A = center_A + vec_lr_A/2 - vec_bt_A/2
        p2_A = center_A + vec_lr_A/2 + vec_bt_A/2
        p3_A = center_A - vec_lr_A/2 + vec_bt_A/2
        
        center_B = np.array([1.35, 0.75, 0])
        vec_lr_B = np.array([2.7, -1.5, 0])
        vec_bt_B = np.array([0, 0, 1.9])
        
        p0_B = center_B - vec_lr_B/2 - vec_bt_B/2
        p1_B = center_B + vec_lr_B/2 - vec_bt_B/2
        p2_B = center_B + vec_lr_B/2 + vec_bt_B/2
        p3_B = center_B - vec_lr_B/2 + vec_bt_B/2

        poly_A = Polygon(p0_A, p1_A, p2_A, p3_A, fill_color=pink_color, fill_opacity=0.18, stroke_width=0)
        poly_B = Polygon(p0_B, p1_B, p2_B, p3_B, fill_color=purple_color, fill_opacity=0.18, stroke_width=0)

        arr_l_A = CameraFacingArrow(p0_A, p3_A, pink_color, 0.25, cam_dir_3d)
        arr_r_B = CameraFacingArrow(p2_B, p1_B, purple_color, 0.25, cam_dir_3d)
        
        top_yellow_arrow = CameraFacingArrow(p3_A, p2_B, SAT_YELLOW, 0.25, cam_dir_3d)
        bot_yellow_arrow = CameraFacingArrow(p1_B, p0_A, SAT_YELLOW, 0.25, cam_dir_3d)
        
        yellow_poly = Polygon(p0_A, p1_B, p2_B, p3_A, fill_color=SAT_YELLOW, fill_opacity=0.18, stroke_width=0)
        
        w_C = np.linalg.norm(p1_B - p0_A)
        h_C = np.linalg.norm(p3_A - p0_A)
        target_x_C = (p1_B - p0_A) / w_C
        target_y_C = (p3_A - p0_A) / h_C
        target_z_C = np.cross(target_x_C, target_y_C)
        matrix_C = np.column_stack((target_x_C, target_y_C, target_z_C))
        
        # Hardcoded at scale 1.2 to perfectly match the ending of Scene 11
        label_C = MathTex(r"\bivec{A} + \bivec{B}", color=SAT_YELLOW, tex_template=custom_template).scale(1.2)
        center_bot = (p0_A + p1_B) / 2
        label_C.apply_matrix(matrix_C)
        label_C.move_to(center_bot + target_y_C * (-0.45))
        
        label_A = MathTex(r"\bivec{A}", color=pink_color, tex_template=custom_template).scale(1.2)
        target_x_A = vec_lr_A / np.linalg.norm(vec_lr_A)
        target_y_A = vec_bt_A / np.linalg.norm(vec_bt_A)
        target_z_A = np.cross(target_x_A, target_y_A)
        matrix_A = np.column_stack((target_x_A, target_y_A, target_z_A))
        label_A.apply_matrix(matrix_A)
        label_A.move_to(p3_A + target_x_A * (-0.35) + target_y_A * (0.45))
        
        label_B = MathTex(r"\bivec{B}", color=purple_color, tex_template=custom_template).scale(1.2)
        target_x_B = vec_lr_B / np.linalg.norm(vec_lr_B)
        target_y_B = vec_bt_B / np.linalg.norm(vec_bt_B)
        target_z_B = np.cross(target_x_B, target_y_B)
        matrix_B = np.column_stack((target_x_B, target_y_B, target_z_B))
        label_B.apply_matrix(matrix_B)
        label_B.move_to(p2_B + target_x_B * (0.35) + target_y_B * (0.45))
        
        scene_11_objects = VGroup(
            poly_A, poly_B,
            yellow_poly, arr_l_A, arr_r_B, top_yellow_arrow, bot_yellow_arrow, 
            label_C, label_A, label_B
        )
        self.add(scene_11_objects)

        # ----------------------------------------------------
        # t = 15.98s (6:37:21): Reset into Parallelograms
        # ----------------------------------------------------
        self.wait(15.98)
        
        def make_arrow(start, end, color):
            start_arr = np.array(start)
            end_arr = np.array(end)
            length = np.linalg.norm(end_arr - start_arr)
            return Arrow(start_arr, end_arr, buff=0, color=color, stroke_width=6, max_tip_length_to_length_ratio=0.25/length)

        D0 = np.array([-4.0, -0.2, 0])
        D1 = np.array([-1.3, -0.2, 0])
        D2 = np.array([0.1, 1.7, 0])
        D3 = np.array([-2.6, 1.7, 0])
        
        para_L_poly = Polygon(D0, D1, D2, D3, fill_color=ORANGE, fill_opacity=0.18, stroke_width=0)
        para_L_bot = make_arrow(D0, D1, purple_color)
        para_L_left = make_arrow(D3, D0, pink_color)
        para_L_top = make_arrow(D2, D3, purple_color)
        para_L_right = make_arrow(D1, D2, pink_color)
        para_L_group = VGroup(para_L_poly, para_L_bot, para_L_left, para_L_top, para_L_right)
        
        C0 = np.array([0.5, -0.2, 0])
        C1 = np.array([1.9, 1.7, 0])
        C2 = np.array([4.6, 1.7, 0])
        C3 = np.array([3.2, -0.2, 0])
        
        para_R_poly = Polygon(C0, C1, C2, C3, fill_color=ORANGE, fill_opacity=0.18, stroke_width=0)
        para_R_bot = make_arrow(C3, C0, purple_color)
        para_R_left = make_arrow(C0, C1, pink_color)
        para_R_top = make_arrow(C1, C2, purple_color)
        para_R_right = make_arrow(C2, C3, pink_color)
        para_R_group = VGroup(para_R_poly, para_R_bot, para_R_left, para_R_top, para_R_right)

        # Equations utilize the 0.85 SCALE_FACTOR explicitly
        label_L = MathTex(r"-", r"\vec{a}", r"\wedge", r"\vec{b}").scale(SCALE_FACTOR)
        label_L[1].set_color(pink_color)
        label_L[3].set_color(purple_color)
        label_L.next_to(para_L_group, UP, buff=0.25)
        
        label_R = MathTex(r"\vec{a}", r"\wedge", r"\vec{b}").scale(SCALE_FACTOR)
        label_R[0].set_color(pink_color)
        label_R[2].set_color(purple_color)
        label_R.next_to(para_R_group, UP, buff=0.25)
        label_R.set_y(label_L.get_y())

        self.move_camera(
            phi=0 * DEGREES, 
            theta=-90 * DEGREES,
            added_anims=[
                FadeOut(scene_11_objects),
                FadeIn(para_L_group),
                FadeIn(para_R_group),
                FadeIn(label_L),
                FadeIn(label_R)
            ],
            run_time=1.5
        )

        # ----------------------------------------------------
        # t = 19.83s (6:41:12): Overlap Parallelograms
        # ----------------------------------------------------
        self.wait(2.35)
        
        edge_vec = D2 - D1
        normal_vec = np.array([-edge_vec[1], edge_vec[0], 0])
        normal_unit = normal_vec / np.linalg.norm(normal_vec)
        
        touch_offset = normal_unit * 0.025
        
        target_center_L = np.array([0.3, 0.75, 0]) + touch_offset
        target_center_R = np.array([0.3, 0.75, 0]) - touch_offset
        
        current_center_L = np.array([-1.95, 0.75, 0])
        current_center_R = np.array([2.55, 0.75, 0])
        
        shift_L = target_center_L - current_center_L
        shift_R = target_center_R - current_center_R
        
        label_y = label_L.get_y()
        
        self.play(
            para_L_group.animate.shift(shift_L),
            para_R_group.animate.shift(shift_R),
            label_L.animate.move_to(np.array([0.3 - 1.5, label_y, 0])),
            label_R.animate.move_to(np.array([0.3 + 1.5, label_y, 0])),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 22.65s (6:44:01): Shrink and Cancel Edges
        # ----------------------------------------------------
        self.wait(1.82)
        
        def cancel_edge(edge_L, edge_R, is_last=False):
            v_shrink = ValueTracker(0)
            orig_start_L, orig_end_L = edge_L.get_start(), edge_L.get_end()
            orig_start_R, orig_end_R = edge_R.get_start(), edge_R.get_end()
            
            center_pt = (orig_start_L + orig_end_L) / 2
            
            def update_L(m):
                v = min(v_shrink.get_value(), 0.95) 
                m.put_start_and_end_on(interpolate(orig_start_L, center_pt, v), interpolate(orig_end_L, center_pt, v))
                
            def update_R(m):
                v = min(v_shrink.get_value(), 0.95)
                m.put_start_and_end_on(interpolate(orig_start_R, center_pt, v), interpolate(orig_end_R, center_pt, v))
                
            edge_L.add_updater(update_L)
            edge_R.add_updater(update_R)
            
            self.play(v_shrink.animate.set_value(1.0), run_time=0.72)
            edge_L.clear_updaters()
            edge_R.clear_updaters()
            
            self.play(
                edge_L.animate.set_color(WHITE),
                edge_R.animate.set_color(WHITE),
                run_time=0.18
            )
            
            if is_last:
                self.play(
                    FadeOut(edge_L), FadeOut(edge_R),
                    FadeOut(para_L_poly), FadeOut(para_R_poly),
                    run_time=0.18
                )
            else:
                self.play(
                    FadeOut(edge_L), FadeOut(edge_R),
                    run_time=0.18
                )

        cancel_edge(para_L_top, para_R_top, is_last=False)
        cancel_edge(para_L_right, para_R_right, is_last=False)
        cancel_edge(para_L_bot, para_R_bot, is_last=False)
        cancel_edge(para_L_left, para_R_left, is_last=True)

        # ----------------------------------------------------
        # Write Final Equation (-a \wedge b + a \wedge b = 0)
        # ----------------------------------------------------
        plus = MathTex("+", tex_template=custom_template).scale(SCALE_FACTOR)
        equals_zero = MathTex("= 0", tex_template=custom_template).scale(SCALE_FACTOR)
        
        eq_scene12 = VGroup(label_L.copy(), plus, label_R.copy(), equals_zero).arrange(RIGHT, buff=0.2)
        eq_scene12.move_to(np.array([0.3, label_y, 0]))

        self.play(
            label_L.animate.move_to(eq_scene12[0]),
            label_R.animate.move_to(eq_scene12[2]),
            FadeIn(plus.move_to(eq_scene12[1])),
            FadeIn(equals_zero.move_to(eq_scene12[3])),
            run_time=2.5
        )
        
        # ----------------------------------------------------
        # t = 30.75s (6:52:07): Transform to (a \wedge b)^2 \le 0 ??
        # ----------------------------------------------------
        self.wait(1.28)
        
        eq_new_top = MathTex(r"(", r"\vec{a}", r"\wedge", r"\vec{b}", r")^2", r"\le 0", r"\text{ ??}", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_new_top[1].set_color(pink_color)
        eq_new_top[3].set_color(purple_color)
        eq_new_top.move_to(np.array([0.0, label_y, 0]))
        
        self.play(
            ReplacementTransform(label_L, eq_new_top[1:4]),
            ReplacementTransform(label_R, eq_new_top[1:4]),
            FadeOut(plus), FadeOut(equals_zero),
            FadeIn(eq_new_top[0]), FadeIn(eq_new_top[4]), FadeIn(eq_new_top[5]), FadeIn(eq_new_top[6]),
            run_time=1.0
        )
        
        footnote = Tex(
            r"\parbox{15cm}{\centering *I use $\tav$ as the circle constant that is the number of radians in a circle, or $\tav = 2\pi$. $\tau$ has too many other uses to serve this universal purpose. I know it's annoying at first, but it's a better way to think about circles imo. xkcd 927 relevant as ever.}",
            tex_template=custom_template,
            font_size=24,
            color=GRAY
        ).to_edge(DOWN, buff=0.2)

        dummy_top = MathTex(r"(", r"\vec{a}", r"\wedge", r"\vec{b}", r")^2", r"\le 0", r"\text{ ??}", tex_template=custom_template).scale(SCALE_FACTOR)
        dummy_top.move_to(np.array([0.0, 2.0, 0]))

        eq_line4_left = MathTex(r"\vec{x} \parallel \vec{y} \implies", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line4_mid1 = MathTex(r"|\vec{x} \wedge \vec{y}| = x y \sin \theta", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line4_mid2 = MathTex(r"= x y \sin(0)", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line4_right = MathTex(r"= x y \sin\left(\frac{\tav}{2}\right) = 0", tex_template=custom_template).scale(SCALE_FACTOR)
        
        full_line4_dummy = VGroup(eq_line4_left.copy(), eq_line4_mid1.copy(), eq_line4_mid2.copy(), eq_line4_right.copy()).arrange(RIGHT, buff=0.2)
        full_line4_dummy.set_x(0)
        target_left_x = full_line4_dummy[0].get_left()[0]

        # ----------------------------------------------------
        # t = 35.00s (6:56:22): write out xy = x dot y + x wedge y
        # ----------------------------------------------------
        self.wait(3.25)
        
        eq_line2 = MathTex(r"\vec{x}\vec{y} = \vec{x} \cdot \vec{y} + \vec{x} \wedge \vec{y}", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line2.next_to(dummy_top, DOWN, buff=0.5)
        
        self.play(Write(eq_line2), run_time=1.0)
        
        # ----------------------------------------------------
        # t = 39.82s (7:01:11): write \vec{x} \perp \vec{y} \implies \vec{x} \cdot \vec{y} = x y \cos \theta
        # ----------------------------------------------------
        self.wait(3.82)
        
        eq_line3_left = MathTex(r"\vec{x} \perp \vec{y} \implies", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line3_mid = MathTex(r"\vec{x} \cdot \vec{y} = x y \cos \theta", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line3_right = MathTex(r"= x y \cos\left(\frac{\tav}{4}\right) = 0", tex_template=custom_template).scale(SCALE_FACTOR)
        
        full_line3 = VGroup(eq_line3_left, eq_line3_mid, eq_line3_right).arrange(RIGHT, buff=0.2)
        full_line3.next_to(eq_line2, DOWN, buff=0.5)
        full_line3.set_x(target_left_x, direction=LEFT) 
        
        self.play(Write(eq_line3_left), Write(eq_line3_mid), run_time=1.0)
        
        # ----------------------------------------------------
        # t = 45.73s (7:07:06): continue the line with = x y \cos(\tav/4) = 0
        # ----------------------------------------------------
        self.wait(4.91)

        self.play(Write(eq_line3_right), FadeIn(footnote), run_time=1.0)
        
        # ----------------------------------------------------
        # t = 49.68s (7:11:03): replace right side with \vec{x}\vec{y} = \vec{x} \wedge \vec{y}
        # ----------------------------------------------------
        self.wait(2.95)
        
        eq_line3_new_mid = MathTex(r"\vec{x}\vec{y} = \vec{x} \wedge \vec{y}", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line3_new_mid.next_to(eq_line3_left, RIGHT, buff=0.2)
        
        self.play(
            ReplacementTransform(VGroup(eq_line3_mid, eq_line3_right), eq_line3_new_mid),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 54.63s (7:16:00): write \vec{x} \parallel \vec{y} \implies |\vec{x} \wedge \vec{y}| = x y \sin \theta
        # ----------------------------------------------------
        self.wait(3.95)

        full_line4 = VGroup(eq_line4_left, eq_line4_mid1, eq_line4_mid2, eq_line4_right).arrange(RIGHT, buff=0.2)
        full_line4.next_to(eq_line3_left, DOWN, buff=0.5)
        full_line4.set_x(target_left_x, direction=LEFT) 

        self.play(Write(eq_line4_left), Write(eq_line4_mid1), run_time=1.0)
        
        # ----------------------------------------------------
        # t = 59.63s (7:21:00): append = x y \sin(0) and = x y \sin(\tav / 2) = 0
        # ----------------------------------------------------
        self.wait(4.00)

        self.play(Write(eq_line4_mid2), run_time=0.75)
        self.play(Write(eq_line4_right), run_time=0.75)

        # ----------------------------------------------------
        # t = 65.68s (7:27:03): replace right side with \vec{x}\vec{y} = \vec{x} \cdot \vec{y}
        # ----------------------------------------------------
        self.wait(4.55)

        eq_line4_new_mid = MathTex(r"\vec{x}\vec{y} = \vec{x} \cdot \vec{y}", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line4_new_mid.next_to(eq_line4_left, RIGHT, buff=0.2)

        self.play(
            ReplacementTransform(VGroup(eq_line4_mid1, eq_line4_mid2, eq_line4_right), eq_line4_new_mid),
            FadeOut(footnote),
            run_time=1.0
        )

        # ----------------------------------------------------
        # Tail Buffer
        # ----------------------------------------------------
        self.wait(10.0)
        
        
class Scene13(Scene):
    def construct(self):
        custom_template = TexTemplate()
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}")
        custom_template.add_to_preamble(r"\usepackage{accents}")
        custom_template.add_to_preamble(r"\usepackage{cjhebrew}")
        custom_template.add_to_preamble(r"\newcommand{\tav}{\text{\cjhebrew{t}}}")
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        pink_color = "#FF66B2"     
        purple_color = "#A468FF"   
        SCALE_FACTOR = 0.85

        # ----------------------------------------------------
        # t = 0.00s (7:31:07): Start Scene 13
        # Recreate exact Final Frame of Scene 12
        # ----------------------------------------------------
        
        # Recreate Scene 12's exact dummy coordinates to extract the matching label_y
        D0_dummy = np.array([-4.0, -0.2, 0])
        D1_dummy = np.array([-1.3, -0.2, 0])
        D2_dummy = np.array([0.1, 1.7, 0])
        D3_dummy = np.array([-2.6, 1.7, 0])
        
        para_dummy_poly = Polygon(D0_dummy, D1_dummy, D2_dummy, D3_dummy, stroke_width=0)
        arrow_len = np.linalg.norm(D3_dummy - D2_dummy)
        para_dummy_top = Arrow(D2_dummy, D3_dummy, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25/arrow_len)
        para_dummy_group = VGroup(para_dummy_poly, para_dummy_top)
        
        dummy_label_L = MathTex(r"-", r"\vec{a}", r"\wedge", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        dummy_label_L.next_to(para_dummy_group, UP, buff=0.25)
        label_y = dummy_label_L.get_y()

        eq_new_top = MathTex(r"(", r"\vec{a}", r"\wedge", r"\vec{b}", r")^2", r"\le 0", r"\text{ ??}", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_new_top[1].set_color(pink_color)
        eq_new_top[3].set_color(purple_color)
        eq_new_top.move_to(np.array([0.0, label_y, 0]))

        dummy_top = MathTex(r"(", r"\vec{a}", r"\wedge", r"\vec{b}", r")^2", r"\le 0", r"\text{ ??}", tex_template=custom_template).scale(SCALE_FACTOR)
        dummy_top.move_to(np.array([0.0, 2.0, 0]))

        d_eq_line4_left = MathTex(r"\vec{x} \parallel \vec{y} \implies", tex_template=custom_template).scale(SCALE_FACTOR)
        d_eq_line4_mid1 = MathTex(r"|\vec{x} \wedge \vec{y}| = x y \sin \theta", tex_template=custom_template).scale(SCALE_FACTOR)
        d_eq_line4_mid2 = MathTex(r"= x y \sin(0)", tex_template=custom_template).scale(SCALE_FACTOR)
        d_eq_line4_right = MathTex(r"= x y \sin\left(\frac{\tav}{2}\right) = 0", tex_template=custom_template).scale(SCALE_FACTOR)
        
        full_line4_dummy = VGroup(d_eq_line4_left, d_eq_line4_mid1, d_eq_line4_mid2, d_eq_line4_right).arrange(RIGHT, buff=0.2)
        full_line4_dummy.set_x(0)
        target_left_x = full_line4_dummy[0].get_left()[0]

        eq_line2 = MathTex(r"\vec{x}\vec{y} = \vec{x} \cdot \vec{y} + \vec{x} \wedge \vec{y}", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line2.next_to(dummy_top, DOWN, buff=0.5)

        # Unified single MathTex object to natively inherit exact internal LaTeX spacing
        eq_line3_left = MathTex(r"\vec{x} \perp \vec{y}", r" \implies", tex_template=custom_template).scale(SCALE_FACTOR)
        
        d_eq_line3_mid = MathTex(r"\vec{x} \cdot \vec{y} = x y \cos \theta", tex_template=custom_template).scale(SCALE_FACTOR)
        d_eq_line3_right = MathTex(r"= x y \cos\left(\frac{\tav}{4}\right) = 0", tex_template=custom_template).scale(SCALE_FACTOR)
        
        full_line3_dummy = VGroup(eq_line3_left, d_eq_line3_mid, d_eq_line3_right).arrange(RIGHT, buff=0.2)
        full_line3_dummy.next_to(eq_line2, DOWN, buff=0.5)
        full_line3_dummy.set_x(target_left_x, direction=LEFT)

        eq_line3_new_mid = MathTex(r"\vec{x}\vec{y} = \vec{x} \wedge \vec{y}", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line3_new_mid.next_to(eq_line3_left, RIGHT, buff=0.2)

        eq_line4_left = MathTex(r"\vec{x} \parallel \vec{y} \implies", tex_template=custom_template).scale(SCALE_FACTOR)
        
        full_line4_dummy2 = VGroup(eq_line4_left, d_eq_line4_mid1.copy(), d_eq_line4_mid2.copy(), d_eq_line4_right.copy()).arrange(RIGHT, buff=0.2)
        full_line4_dummy2.next_to(eq_line3_left, DOWN, buff=0.5)
        full_line4_dummy2.set_x(target_left_x, direction=LEFT)

        eq_line4_new_mid = MathTex(r"\vec{x}\vec{y} = \vec{x} \cdot \vec{y}", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_line4_new_mid.next_to(eq_line4_left, RIGHT, buff=0.2)

        self.add(eq_new_top, eq_line2, eq_line3_left, eq_line3_new_mid, eq_line4_left, eq_line4_new_mid)

        # ----------------------------------------------------
        # t = 7.06s (7:38:11): x \perp y moves to top left, rest fades
        # ----------------------------------------------------
        self.wait(6.06)

        cond1 = eq_line3_left[0]
        
        self.play(
            cond1.animate.to_corner(UL, buff=1.0),
            FadeOut(eq_line3_left[1]),
            FadeOut(eq_line3_new_mid),
            FadeOut(eq_new_top),
            FadeOut(eq_line2),
            FadeOut(eq_line4_left),
            FadeOut(eq_line4_new_mid),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 8.95s (7:40:04): append \vec{x}^2 = \vec{y}^2 = 1
        # ----------------------------------------------------
        self.wait(0.88)

        cond2 = MathTex(r"\vec{x}^{\,2} = \vec{y}^{\,2} = 1", tex_template=custom_template).scale(SCALE_FACTOR)
        cond2.next_to(cond1, RIGHT, buff=0.6) 
        
        self.play(Write(cond2), run_time=1.0)

        # ----------------------------------------------------
        # t = 11.15s (7:42:16): write (\vec{x} \wedge \vec{y})^2 below
        # ----------------------------------------------------
        self.wait(1.20)

        d_eq2_left = MathTex(r"(\vec{x} \wedge \vec{y})^2", tex_template=custom_template).scale(SCALE_FACTOR)
        d_eq2_mid1 = MathTex(r"= (\vec{x}\vec{y})^2", tex_template=custom_template).scale(SCALE_FACTOR)
        d_term_eq = MathTex("=", tex_template=custom_template).scale(SCALE_FACTOR)
        d_term_x1 = MathTex(r"\vec{x}", tex_template=custom_template).scale(SCALE_FACTOR)
        d_term_y1 = MathTex(r"\vec{y}", tex_template=custom_template).scale(SCALE_FACTOR)
        d_term_x2 = MathTex(r"\vec{x}", tex_template=custom_template).scale(SCALE_FACTOR)
        d_term_y2 = MathTex(r"\vec{y}", tex_template=custom_template).scale(SCALE_FACTOR)
        
        d_xyxy = VGroup(d_term_x1, d_term_y1, d_term_x2, d_term_y2).arrange(RIGHT, buff=0.08)
        dummy_full_line = VGroup(d_eq2_left, d_eq2_mid1, d_term_eq, d_xyxy).arrange(RIGHT, buff=0.2)
        dummy_full_line.move_to(UP * 0.5)

        eq2_left = d_eq2_left.copy()
        eq2_mid1 = d_eq2_mid1.copy()
        term_eq = d_term_eq.copy()
        term_x1 = d_term_x1.copy()
        term_y1 = d_term_y1.copy()
        term_x2 = d_term_x2.copy()
        term_y2 = d_term_y2.copy()

        self.play(Write(eq2_left), run_time=1.0)

        # ----------------------------------------------------
        # t = 13.01s (7:44:08): append = (\vec{x}\vec{y})^2
        # ----------------------------------------------------
        self.wait(0.86)
        
        self.play(Write(eq2_mid1), run_time=1.0)

        # ----------------------------------------------------
        # t = 15.01s (7:46:08): append = \vec{x}\vec{y}\vec{x}\vec{y}
        # ----------------------------------------------------
        self.wait(1.00)

        self.play(
            Write(term_eq),
            Write(term_x1), Write(term_y1), Write(term_x2), Write(term_y2),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 18.93s (7:50:03): Space out \vec{x} \quad \vec{y}\vec{x} \quad \vec{y}
        # ----------------------------------------------------
        self.wait(2.92)

        shift_amt = 0.4
        self.play(
            term_y1.animate.shift(RIGHT * shift_amt),
            term_x2.animate.shift(RIGHT * shift_amt),
            term_y2.animate.shift(RIGHT * 2 * shift_amt),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 21.01s (7:52:08): Alter middle letters to \vec{y} \wedge \vec{x}
        # ----------------------------------------------------
        self.wait(1.08)

        term_wedge = MathTex(r"\wedge", tex_template=custom_template).scale(SCALE_FACTOR)
        term_wedge.move_to(VGroup(term_y1, term_x2))
        w_width = term_wedge.width + 0.1

        self.play(
            term_y1.animate.shift(LEFT * w_width/2),
            term_x2.animate.shift(RIGHT * w_width/2),
            term_y2.animate.shift(RIGHT * w_width/2),
            FadeIn(term_wedge),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 23.91s (7:55:02): Rigidly swap \vec{y} \wedge \vec{x} into -\vec{x} \wedge \vec{y}
        # ----------------------------------------------------
        self.wait(1.90)

        term_minus = MathTex("-", tex_template=custom_template).scale(SCALE_FACTOR)
        
        dummy_swap = VGroup(term_minus, term_x2.copy(), term_wedge.copy(), term_y1.copy()).arrange(RIGHT, buff=0.08)
        dummy_swap.next_to(term_x1, RIGHT, buff=shift_amt)
        
        delta_x = dummy_swap[-1].get_right()[0] - term_x2.get_right()[0]
        term_minus.move_to(dummy_swap[0])

        self.play(
            FadeIn(term_minus),
            term_x2.animate.move_to(dummy_swap[1]),
            term_wedge.animate.move_to(dummy_swap[2]),
            term_y1.animate.move_to(dummy_swap[3]),
            term_y2.animate.shift(RIGHT * delta_x),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 26.20s (7:57:19): Turn \vec{x} \wedge \vec{y} into \vec{x}\vec{y} and send minus sign to front
        # ----------------------------------------------------
        self.wait(1.29)

        target_minus = term_minus.generate_target()
        target_x1 = term_x1.generate_target()
        target_x2 = term_x2.generate_target()
        target_y1 = term_y1.generate_target()
        target_y2 = term_y2.generate_target()
        
        target_minus.next_to(term_eq, RIGHT, buff=0.2)
        target_x1.next_to(target_minus, RIGHT, buff=0.05) 
        target_x2.next_to(target_x1, RIGHT, buff=shift_amt)
        target_y1.next_to(target_x2, RIGHT, buff=0.08)
        target_y2.next_to(target_y1, RIGHT, buff=shift_amt)
        
        self.play(
            FadeOut(term_wedge),
            MoveToTarget(term_minus),
            MoveToTarget(term_x1),
            MoveToTarget(term_x2),
            MoveToTarget(term_y1),
            MoveToTarget(term_y2),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 29.08s (8:00:16): Bring text back together to normal spacing -\vec{x}\vec{x}\vec{y}\vec{y}
        # ----------------------------------------------------
        self.wait(1.88)

        target_minus2 = term_minus.generate_target()
        target_x1_2 = term_x1.generate_target()
        target_x2_2 = term_x2.generate_target()
        target_y1_2 = term_y1.generate_target()
        target_y2_2 = term_y2.generate_target()
        
        target_minus2.next_to(term_eq, RIGHT, buff=0.2)
        VGroup(target_x1_2, target_x2_2, target_y1_2, target_y2_2).arrange(RIGHT, buff=0.08).next_to(target_minus2, RIGHT, buff=0.05)
        
        self.play(
            MoveToTarget(term_minus),
            MoveToTarget(term_x1),
            MoveToTarget(term_x2),
            MoveToTarget(term_y1),
            MoveToTarget(term_y2),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 30.98s (8:02:06): xx collapses to 1, yy collapses to *1
        # ----------------------------------------------------
        self.wait(0.90)

        term_1a = MathTex("1", tex_template=custom_template).scale(SCALE_FACTOR)
        term_dot = MathTex(r"\cdot", tex_template=custom_template).scale(SCALE_FACTOR)
        term_1b = MathTex("1", tex_template=custom_template).scale(SCALE_FACTOR)
        
        dummy_ones = VGroup(term_1a, term_dot, term_1b).arrange(RIGHT, buff=0.2)
        dummy_ones.next_to(term_minus, RIGHT, buff=0.05)

        self.play(
            ReplacementTransform(VGroup(term_x1, term_x2), term_1a),
            ReplacementTransform(VGroup(term_y1, term_y2), VGroup(term_dot, term_1b)),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 33.97s (8:05:05): -1 * 1 becomes -1
        # ----------------------------------------------------
        self.wait(1.99)

        self.play(
            FadeOut(term_dot),
            term_1b.animate.move_to(term_1a),
            run_time=1.0
        )
        self.remove(term_1b)

        # ----------------------------------------------------
        # t = 43.16s (8:14:17): (x \wedge y)^2 rises, others fade, append = -|x \wedge y|^2
        # ----------------------------------------------------
        self.wait(8.19)

        new_rhs = MathTex(r"= -|\vec{x} \wedge \vec{y}|^2", tex_template=custom_template).scale(SCALE_FACTOR)
        
        dummy_new_line = VGroup(eq2_left.copy(), new_rhs).arrange(RIGHT, buff=0.2)
        dummy_new_line.move_to(UP * 1.5)

        self.play(
            eq2_left.animate.move_to(dummy_new_line[0]),
            FadeOut(cond1),
            FadeOut(cond2),
            FadeOut(eq2_mid1),
            FadeOut(term_eq),
            FadeOut(term_minus),
            FadeOut(term_1a),
            Write(new_rhs.move_to(dummy_new_line[1])),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 47.88s (8:19:00): write \vec{v}^2 = |\vec{v}|^2 below
        # ----------------------------------------------------
        self.wait(3.72)

        eq_v = MathTex(r"\vec{v}^2 = |\vec{v}|^2", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_v.next_to(dummy_new_line, DOWN, buff=0.8)

        self.play(Write(eq_v), run_time=1.0)

        # ----------------------------------------------------
        # Tail Buffer
        # ----------------------------------------------------
        self.wait(10.0)
        


class Scene14(Scene):
    def construct(self):
        custom_template = TexTemplate()
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}")
        custom_template.add_to_preamble(r"\usepackage{accents}")
        custom_template.add_to_preamble(r"\usepackage{cjhebrew}")
        custom_template.add_to_preamble(r"\newcommand{\tav}{\text{\cjhebrew{t}}}")
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        pink_color = "#FF66B2"     
        purple_color = "#A468FF"
        brown_fill = "#4B3621"
        SCALE_FACTOR = 0.85

        # ----------------------------------------------------
        # t = 0.00s (8:24:08): Start Scene 14
        # Recreate exact Final Frame of Scene 13
        # ----------------------------------------------------
        
        d_eq2_left = MathTex(r"(\vec{x} \wedge \vec{y})^2", tex_template=custom_template).scale(SCALE_FACTOR)
        new_rhs = MathTex(r"= -|\vec{x} \wedge \vec{y}|^2", tex_template=custom_template).scale(SCALE_FACTOR)
        dummy_new_line = VGroup(d_eq2_left, new_rhs).arrange(RIGHT, buff=0.2)
        dummy_new_line.move_to(UP * 1.5)

        eq2_left = d_eq2_left.copy()
        new_rhs_copy = new_rhs.copy()

        eq_v = MathTex(r"\vec{v}^2 = |\vec{v}|^2", tex_template=custom_template).scale(SCALE_FACTOR)
        eq_v.next_to(dummy_new_line, DOWN, buff=0.8)

        self.add(eq2_left, new_rhs_copy, eq_v)

        # ----------------------------------------------------
        # t = 5.99s (8:30:07): Scroll prism up into second screen
        # ----------------------------------------------------
        self.wait(5.99)

        new_lhs = MathTex(r"\vec{a}", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        new_lhs[0].set_color(pink_color)
        new_lhs[1].set_color(purple_color)
        
        new_rhs_app = MathTex(r"=", r"\vec{a}", r"\cdot", r"\vec{b}", r"+", r"\vec{a}", r"\wedge", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        new_rhs_app[1].set_color(pink_color)
        new_rhs_app[3].set_color(purple_color)
        new_rhs_app[5].set_color(pink_color)
        new_rhs_app[7].set_color(purple_color)

        final_eq = VGroup(new_lhs, new_rhs_app).arrange(RIGHT, buff=0.2)
        final_eq.move_to(UP * 1.5)

        screen1 = VGroup(eq2_left, new_rhs_copy, eq_v)
        screen2 = final_eq

        R = 1.5
        rot_center = screen1.get_center() + IN * R
        
        screen2.rotate(PI/2, axis=RIGHT, about_point=rot_center)
        screen2.set_opacity(0)
        self.add(screen2)

        screen1.save_state()
        screen2.save_state()

        def update_screen1(mob, alpha):
            mob.restore()
            mob.rotate(-alpha * PI/2, axis=RIGHT, about_point=rot_center)
            mob.set_opacity(1 - alpha)
            
        def update_screen2(mob, alpha):
            mob.restore()
            mob.rotate(-alpha * PI/2, axis=RIGHT, about_point=rot_center)
            mob.set_opacity(alpha)

        self.play(
            UpdateFromAlphaFunc(screen1, update_screen1),
            UpdateFromAlphaFunc(screen2, update_screen2),
            run_time=1.2
        )

        # ----------------------------------------------------
        # Setup Vectors and Geometry natively scaled
        # ----------------------------------------------------
        vec_a_dir = RIGHT * 0.75 + UP * 1.0
        vec_b_dir = RIGHT * 1.25

        # 1. Pink vector a
        vec_a = Arrow(ORIGIN, vec_a_dir, buff=0, color=pink_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)

        # 2. Purple vector b
        vec_b = Arrow(ORIGIN, vec_b_dir, buff=0, color=purple_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)

        # 3. Yin-yang swirl
        yin_yang = VGroup()
        left_half = Arc(radius=0.5, start_angle=PI/2, angle=PI, fill_opacity=1, color=pink_color, stroke_width=0)
        right_half = Arc(radius=0.5, start_angle=-PI/2, angle=PI, fill_opacity=1, color=purple_color, stroke_width=0)
        top_circle = Circle(radius=0.25, fill_opacity=1, color=pink_color, stroke_width=0).shift(UP * 0.25)
        bottom_circle = Circle(radius=0.25, fill_opacity=1, color=purple_color, stroke_width=0).shift(DOWN * 0.25)
        yin_yang.add(left_half, right_half, top_circle, bottom_circle).scale(0.25)

        # 4. Parallelogram (bivector)
        C0 = ORIGIN
        C1 = C0 + vec_a_dir
        C2 = C1 + vec_b_dir
        C3 = C0 + vec_b_dir
        
        p_area = Polygon(
            C0, C1, C2, C3, 
            fill_opacity=0.8, 
            stroke_width=0
        ).set_fill(brown_fill)
        
        p_vec_1 = Arrow(C0, C1, buff=0, color=pink_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        p_vec_2 = Arrow(C1, C2, buff=0, color=purple_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        p_vec_3 = Arrow(C2, C3, buff=0, color=pink_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        p_vec_4 = Arrow(C3, C0, buff=0, color=purple_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        
        para_group = VGroup(p_area, p_vec_1, p_vec_2, p_vec_3, p_vec_4)

        # 5. Math Operators
        op_times = MathTex(r"\times").scale(1.2)
        op_eq = MathTex("=").scale(1.2)
        op_plus = MathTex("+").scale(1.2)

        # ----------------------------------------------------
        # Position Elements Symmetrically
        # ----------------------------------------------------
        target_y = -1.3
        op_eq.move_to(np.array([0, target_y, 0]))

        vec_b.next_to(op_eq, LEFT, buff=1.0)
        yin_yang.next_to(op_eq, RIGHT, buff=1.0)
        
        op_times.next_to(vec_b, LEFT, buff=0.8)
        vec_a.next_to(op_times, LEFT, buff=0.8)
        
        op_plus.next_to(yin_yang, RIGHT, buff=0.8)
        para_group.next_to(op_plus, RIGHT, buff=0.8)

        for mob in [vec_a, op_times, vec_b, op_eq, yin_yang, op_plus, para_group]:
            mob.set_y(target_y)

        # ----------------------------------------------------
        # Setup Bottom Labels
        # ----------------------------------------------------
        lbl_a = MathTex(r"\vec{a}", tex_template=custom_template, color=pink_color)
        lbl_b = MathTex(r"\vec{b}", tex_template=custom_template, color=purple_color)
        
        lbl_dot = MathTex(r"\vec{a}", r"\cdot", r"\vec{b}", tex_template=custom_template)
        lbl_dot[0].set_color(pink_color)
        lbl_dot[2].set_color(purple_color)
        
        lbl_wedge = MathTex(r"\vec{a}", r"\wedge", r"\vec{b}", tex_template=custom_template)
        lbl_wedge[0].set_color(pink_color)
        lbl_wedge[2].set_color(purple_color)

        label_y = -2.6
        lbl_a.move_to(np.array([vec_a.get_x(), label_y, 0]))
        lbl_b.move_to(np.array([vec_b.get_x(), label_y, 0]))
        lbl_dot.move_to(np.array([yin_yang.get_x(), label_y, 0]))
        lbl_wedge.move_to(np.array([para_group.get_x(), label_y, 0]))

        # ----------------------------------------------------
        # t = 10.15s (8:34:23): Pink vector a appears
        # ----------------------------------------------------
        self.wait(2.96)
        self.play(FadeIn(vec_a), FadeIn(lbl_a), run_time=0.5)

        # ----------------------------------------------------
        # t = 11.10s (8:35:18): Purple vector b appears
        # ----------------------------------------------------
        self.wait(0.45)
        self.play(FadeIn(vec_b), FadeIn(lbl_b), run_time=0.5)

        # ----------------------------------------------------
        # t = 12.94s (8:37:02): Yin-yang swirl circle appears
        # ----------------------------------------------------
        self.wait(1.34)
        self.play(FadeIn(yin_yang), FadeIn(lbl_dot), run_time=0.18)

        # ----------------------------------------------------
        # t = 13.12s (8:37:20): Parallelogram appears
        # ----------------------------------------------------
        self.play(FadeIn(para_group), FadeIn(lbl_wedge), run_time=0.5)

        # ----------------------------------------------------
        # t = 13.82s: Operators simultaneously appear
        # ----------------------------------------------------
        self.wait(0.2)
        self.play(
            FadeIn(op_times),
            FadeIn(op_eq),
            FadeIn(op_plus),
            run_time=0.5
        )

        # ----------------------------------------------------
        # Tail Buffer
        # ----------------------------------------------------
        self.wait(15.0)
 


class Scene15(Scene):
    def construct(self):
        custom_template = TexTemplate()
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}")
        custom_template.add_to_preamble(r"\usepackage{accents}")
        custom_template.add_to_preamble(r"\usepackage{cjhebrew}")
        custom_template.add_to_preamble(r"\newcommand{\tav}{\text{\cjhebrew{t}}}")
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        pink_color = "#FF66B2"     
        purple_color = "#A468FF"
        brown_fill = "#4B3621"
        SCALE_FACTOR = 0.85

        # ----------------------------------------------------
        # t = 0.00s (8:52:16): Start Scene 15
        # Recreate exact Final Frame of Scene 14
        # ----------------------------------------------------
        
        new_lhs = MathTex(r"\vec{a}", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        new_lhs[0].set_color(pink_color)
        new_lhs[1].set_color(purple_color)
        
        new_rhs_app = MathTex(r"=", r"\vec{a}", r"\cdot", r"\vec{b}", r"+", r"\vec{a}", r"\wedge", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        new_rhs_app[1].set_color(pink_color)
        new_rhs_app[3].set_color(purple_color)
        new_rhs_app[5].set_color(pink_color)
        new_rhs_app[7].set_color(purple_color)

        final_eq = VGroup(new_lhs, new_rhs_app).arrange(RIGHT, buff=0.2)
        final_eq.move_to(UP * 1.5)
        self.add(final_eq)

        vec_a_dir = RIGHT * 0.75 + UP * 1.0
        vec_b_dir = RIGHT * 1.25

        vec_a = Arrow(ORIGIN, vec_a_dir, buff=0, color=pink_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        vec_b = Arrow(ORIGIN, vec_b_dir, buff=0, color=purple_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)

        yin_yang = VGroup()
        left_half = Arc(radius=0.5, start_angle=PI/2, angle=PI, fill_opacity=1, color=pink_color, stroke_width=0)
        right_half = Arc(radius=0.5, start_angle=-PI/2, angle=PI, fill_opacity=1, color=purple_color, stroke_width=0)
        top_circle = Circle(radius=0.25, fill_opacity=1, color=pink_color, stroke_width=0).shift(UP * 0.25)
        bottom_circle = Circle(radius=0.25, fill_opacity=1, color=purple_color, stroke_width=0).shift(DOWN * 0.25)
        yin_yang.add(left_half, right_half, top_circle, bottom_circle).scale(0.25)

        C0 = ORIGIN
        C1 = C0 + vec_a_dir
        C2 = C1 + vec_b_dir
        C3 = C0 + vec_b_dir
        
        p_area = Polygon(C0, C1, C2, C3, fill_opacity=0.8, stroke_width=0).set_fill(brown_fill)
        p_vec_1 = Arrow(C0, C1, buff=0, color=pink_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        p_vec_2 = Arrow(C1, C2, buff=0, color=purple_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        p_vec_3 = Arrow(C2, C3, buff=0, color=pink_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        p_vec_4 = Arrow(C3, C0, buff=0, color=purple_color, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        
        para_group = VGroup(p_area, p_vec_1, p_vec_2, p_vec_3, p_vec_4)

        op_times = MathTex(r"\times").scale(1.2)
        op_eq = MathTex("=").scale(1.2)
        op_plus = MathTex("+").scale(1.2)

        target_y = -1.3
        op_eq.move_to(np.array([0, target_y, 0]))

        vec_b.next_to(op_eq, LEFT, buff=1.0)
        yin_yang.next_to(op_eq, RIGHT, buff=1.0)
        
        op_times.next_to(vec_b, LEFT, buff=0.8)
        vec_a.next_to(op_times, LEFT, buff=0.8)
        
        op_plus.next_to(yin_yang, RIGHT, buff=0.8)
        para_group.next_to(op_plus, RIGHT, buff=0.8)

        for mob in [vec_a, op_times, vec_b, op_eq, yin_yang, op_plus, para_group]:
            mob.set_y(target_y)

        lbl_a = MathTex(r"\vec{a}", tex_template=custom_template, color=pink_color)
        lbl_b = MathTex(r"\vec{b}", tex_template=custom_template, color=purple_color)
        lbl_dot = MathTex(r"\vec{a}", r"\cdot", r"\vec{b}", tex_template=custom_template)
        lbl_dot[0].set_color(pink_color)
        lbl_dot[2].set_color(purple_color)
        
        lbl_wedge = MathTex(r"\vec{a}", r"\wedge", r"\vec{b}", tex_template=custom_template)
        lbl_wedge[0].set_color(pink_color)
        lbl_wedge[2].set_color(purple_color)

        label_y = -2.6
        lbl_a.move_to(np.array([vec_a.get_x(), label_y, 0]))
        lbl_b.move_to(np.array([vec_b.get_x(), label_y, 0]))
        lbl_dot.move_to(np.array([yin_yang.get_x(), label_y, 0]))
        lbl_wedge.move_to(np.array([para_group.get_x(), label_y, 0]))

        bottom_elements = VGroup(
            vec_a, op_times, vec_b, op_eq, yin_yang, op_plus, para_group,
            lbl_a, lbl_b, lbl_dot, lbl_wedge
        )
        self.add(bottom_elements)

        # ----------------------------------------------------
        # t = 1.10s (8:53:22): Fade out all but final_eq
        # ----------------------------------------------------
        self.wait(1.10)
        self.play(FadeOut(bottom_elements), run_time=0.5)

        # ----------------------------------------------------
        # t = 2.98s (8:55:15): Write 2 and 3
        # ----------------------------------------------------
        self.wait(1.38)
        
        num_2 = MathTex("2").scale(1.0).move_to(LEFT * 1.5 + UP * 0.8)
        num_3 = MathTex("3").scale(1.0).move_to(RIGHT * 1.5 + UP * 0.8)
        
        self.play(FadeIn(num_2), FadeIn(num_3), run_time=0.5)

        # ----------------------------------------------------
        # t = 3.95s (8:56:13): Two non-parallel vectors x and y
        # ----------------------------------------------------
        self.wait(0.47)
        
        vec_x = Arrow(ORIGIN, RIGHT * 0.8 + UP * 0.8, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        vec_x.move_to(LEFT * 1.5 + DOWN * 0.6)
        lbl_x = MathTex(r"\vec{x}", tex_template=custom_template, color=purple_color).next_to(vec_x, LEFT, buff=0.15)
        grp_x = VGroup(vec_x, lbl_x)

        vec_y = Arrow(ORIGIN, RIGHT * 1.1 + DOWN * 0.4, buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        vec_y.move_to(RIGHT * 1.5 + DOWN * 0.6)
        lbl_y = MathTex(r"\vec{y}", tex_template=custom_template, color=pink_color).next_to(vec_y, RIGHT, buff=0.15)
        grp_y = VGroup(vec_y, lbl_y)

        self.play(FadeIn(grp_x), FadeIn(grp_y), run_time=0.5)

        # ----------------------------------------------------
        # t = 4.88s (8:57:09): Two rectangular bivectors A and B
        # ----------------------------------------------------
        self.wait(0.43)
        
        bivec_y_pos = -2.8
        
        # Bivector A Geometry (Blue, clockwise)
        c_A = np.array([-1.5, bivec_y_pos, 0])
        w_A, h_A = 1.6, 1.1
        A_TL = c_A + LEFT * w_A / 2 + UP * h_A / 2
        A_TR = c_A + RIGHT * w_A / 2 + UP * h_A / 2
        A_BR = c_A + RIGHT * w_A / 2 + DOWN * h_A / 2
        A_BL = c_A + LEFT * w_A / 2 + DOWN * h_A / 2

        area_A = Polygon(A_TL, A_TR, A_BR, A_BL, fill_opacity=0.4, stroke_width=0).set_fill(DARK_BLUE)
        arr_A1 = Arrow(A_TL, A_TR, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A2 = Arrow(A_TR, A_BR, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A3 = Arrow(A_BR, A_BL, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A4 = Arrow(A_BL, A_TL, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        
        lbl_A = MathTex(r"\bivec{A}", tex_template=custom_template, color=BLUE).next_to(area_A, LEFT, buff=0.25)
        grp_A = VGroup(area_A, arr_A1, arr_A2, arr_A3, arr_A4, lbl_A)

        # Bivector B Geometry (Red, clockwise)
        c_B = np.array([1.5, bivec_y_pos, 0])
        w_B, h_B = 1.0, 1.1
        B_TL = c_B + LEFT * w_B / 2 + UP * h_B / 2
        B_TR = c_B + RIGHT * w_B / 2 + UP * h_B / 2
        B_BR = c_B + RIGHT * w_B / 2 + DOWN * h_B / 2
        B_BL = c_B + LEFT * w_B / 2 + DOWN * h_B / 2

        area_B = Polygon(B_TL, B_TR, B_BR, B_BL, fill_opacity=0.4, stroke_width=0).set_fill(DARK_BROWN)
        arr_B1 = Arrow(B_TL, B_TR, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B2 = Arrow(B_TR, B_BR, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B3 = Arrow(B_BR, B_BL, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B4 = Arrow(B_BL, B_TL, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        
        lbl_B = MathTex(r"\bivec{B}", tex_template=custom_template, color=RED).next_to(area_B, RIGHT, buff=0.25)
        grp_B = VGroup(area_B, arr_B1, arr_B2, arr_B3, arr_B4, lbl_B)

        self.play(FadeIn(grp_A), FadeIn(grp_B), run_time=0.5)

        # ----------------------------------------------------
        # t = 6.87s (8:59:03): Pluses appear
        # ----------------------------------------------------
        self.wait(1.49)

        plus_num = MathTex("+").scale(1.0).move_to((num_2.get_center() + num_3.get_center()) / 2)
        plus_vec = MathTex("+").scale(1.0).move_to((grp_x.get_center() + grp_y.get_center()) / 2)
        plus_bivec = MathTex("+").scale(1.0).move_to(np.array([0, bivec_y_pos, 0]))

        self.play(
            FadeIn(plus_num),
            FadeIn(plus_vec),
            FadeIn(plus_bivec),
            run_time=0.5
        )

        # ----------------------------------------------------
        # t = 8.00s (9:00:16): Everything adds together
        # ----------------------------------------------------
        self.wait(0.63)

        num_5 = MathTex("5").scale(1.0).move_to(plus_num.get_center())

        target_vec_peak = np.array([0, -0.2, 0])
        shift_x = target_vec_peak - vec_x.get_end()
        shift_y = target_vec_peak - vec_y.get_start()
        
        vec_sum_start = vec_x.get_start() + shift_x
        vec_sum_end = vec_y.get_end() + shift_y
        
        vec_sum = Arrow(
            vec_sum_start, vec_sum_end, buff=0, color=YELLOW, 
            stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1
        )
        lbl_sum = MathTex(r"\vec{x} + \vec{y}", tex_template=custom_template, color=YELLOW).next_to(vec_sum, RIGHT, buff=0.3)

        shift_A = RIGHT * (0 - (c_A[0] + w_A / 2))
        shift_B = RIGHT * (0 - (c_B[0] - w_B / 2))

        lbl_AB = MathTex(r"\bivec{A} + \bivec{B}", tex_template=custom_template, color=WHITE)
        dummy_combined_right = np.array([w_B, bivec_y_pos, 0])
        lbl_AB.next_to(dummy_combined_right, RIGHT, buff=0.3)

        grp_x.remove(lbl_x)
        grp_y.remove(lbl_y)
        grp_A.remove(lbl_A, arr_A2)
        grp_B.remove(lbl_B, arr_B4)

        self.play(
            ReplacementTransform(VGroup(num_2.copy(), plus_num.copy(), num_3.copy()), num_5),
            num_2.animate.set_opacity(0),
            plus_num.animate.set_opacity(0),
            num_3.animate.set_opacity(0),
            grp_x.animate.shift(shift_x),
            grp_y.animate.shift(shift_y),
            FadeOut(plus_vec),
            FadeOut(lbl_x),
            FadeOut(lbl_y),
            GrowArrow(vec_sum),
            FadeIn(lbl_sum),
            grp_A.animate.shift(shift_A),
            arr_A2.animate.shift(shift_A),
            grp_B.animate.shift(shift_B),
            arr_B4.animate.shift(shift_B),
            FadeOut(plus_bivec),
            FadeOut(lbl_A),
            FadeOut(lbl_B),
            FadeIn(lbl_AB),
            FadeOut(arr_A2),
            FadeOut(arr_B4),
            run_time=1.2
        )

        # ----------------------------------------------------
        # t = 11.57s (9:04:03): Return objects to initial states
        # ----------------------------------------------------
        self.wait(2.37)

        self.play(
            FadeOut(num_5),
            num_2.animate.set_opacity(1),
            plus_num.animate.set_opacity(1),
            num_3.animate.set_opacity(1),
            grp_x.animate.shift(-shift_x),
            grp_y.animate.shift(-shift_y),
            FadeIn(plus_vec),
            FadeIn(lbl_x),
            FadeIn(lbl_y),
            FadeOut(vec_sum),
            FadeOut(lbl_sum),
            grp_A.animate.shift(-shift_A),
            arr_A2.animate.shift(-shift_A),
            grp_B.animate.shift(-shift_B),
            arr_B4.animate.shift(-shift_B),
            FadeIn(plus_bivec),
            FadeIn(lbl_A),
            FadeIn(lbl_B),
            FadeOut(lbl_AB),
            FadeIn(arr_A2),
            FadeIn(arr_B4),
            run_time=1.0
        )

        grp_x.add(lbl_x)
        grp_y.add(lbl_y)
        grp_A.add(lbl_A, arr_A2)
        grp_B.add(lbl_B, arr_B4)

        # ----------------------------------------------------
        # t = 13.77s (9:06:09): Shift left and form equations
        # ----------------------------------------------------
        self.wait(1.20)

        shift_left = LEFT * 4.2

        line_num = VGroup(num_2, plus_num, num_3)
        line_vec = VGroup(grp_x, plus_vec, grp_y)
        line_biv = VGroup(grp_A, plus_bivec, grp_B)

        target_line_num = line_num.copy().shift(shift_left)
        target_line_vec = line_vec.copy().shift(shift_left)
        target_line_biv = line_biv.copy().shift(shift_left)

        max_x = max(target_line_num.get_right()[0], target_line_vec.get_right()[0], target_line_biv.get_right()[0])
        eq_x = max_x + 0.6

        eq_num = MathTex("=").scale(1.0).move_to(np.array([eq_x, num_2.get_y(), 0]))
        num_5_rhs = MathTex("5").scale(1.0).next_to(eq_num, RIGHT, buff=0.6)

        eq_vec = MathTex("=").scale(1.0).move_to(np.array([eq_x, plus_vec.get_y(), 0]))
        
        vec_sum_rhs = vec_sum.copy()
        vec_sum_rhs.next_to(eq_vec, RIGHT, buff=0.6)
        vec_sum_rhs.set_y(eq_vec.get_y() - 0.2)
        
        lbl_sum_rhs = MathTex(r"\vec{x} + \vec{y}", tex_template=custom_template, color=YELLOW).next_to(vec_sum_rhs, RIGHT, buff=0.2)
        vec_sum_group = VGroup(vec_sum_rhs, lbl_sum_rhs)

        eq_biv = MathTex("=").scale(1.0).move_to(np.array([eq_x, plus_bivec.get_y(), 0]))
        RHS_start_x = eq_biv.get_right()[0] + 0.6
        
        AB_TL = np.array([RHS_start_x, bivec_y_pos + h_A/2, 0])
        AB_T_mid = AB_TL + RIGHT * w_A
        AB_TR = AB_T_mid + RIGHT * w_B
        AB_BR = AB_TR + DOWN * h_A
        AB_B_mid = AB_T_mid + DOWN * h_A
        AB_BL = AB_TL + DOWN * h_A

        area_A_rhs = Polygon(AB_TL, AB_T_mid, AB_B_mid, AB_BL, fill_opacity=0.4, stroke_width=0).set_fill(DARK_BLUE)
        area_B_rhs = Polygon(AB_T_mid, AB_TR, AB_BR, AB_B_mid, fill_opacity=0.4, stroke_width=0).set_fill(DARK_BROWN)
        arr_A1_rhs = Arrow(AB_TL, AB_T_mid, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B1_rhs = Arrow(AB_T_mid, AB_TR, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B2_rhs = Arrow(AB_TR, AB_BR, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B3_rhs = Arrow(AB_BR, AB_B_mid, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A3_rhs = Arrow(AB_B_mid, AB_BL, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A4_rhs = Arrow(AB_BL, AB_TL, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)

        biv_sum_rhs = VGroup(area_A_rhs, area_B_rhs, arr_A1_rhs, arr_B1_rhs, arr_B2_rhs, arr_B3_rhs, arr_A3_rhs, arr_A4_rhs)
        lbl_AB_rhs = MathTex(r"\bivec{A} + \bivec{B}", tex_template=custom_template, color=WHITE).next_to(biv_sum_rhs, RIGHT, buff=0.3)
        biv_sum_group = VGroup(biv_sum_rhs, lbl_AB_rhs)

        self.play(
            line_num.animate.shift(shift_left),
            line_vec.animate.shift(shift_left),
            line_biv.animate.shift(shift_left),
            FadeIn(eq_num),
            FadeIn(num_5_rhs),
            FadeIn(eq_vec),
            FadeIn(vec_sum_group),
            FadeIn(eq_biv),
            FadeIn(biv_sum_group),
            run_time=1.2
        )

        # ----------------------------------------------------
        # Tail Buffer
        # ----------------------------------------------------
        self.wait(10.0)
        
        




class Scene16(Scene):
    def construct(self):
        custom_template = TexTemplate()
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}")
        custom_template.add_to_preamble(r"\usepackage{accents}")
        custom_template.add_to_preamble(r"\usepackage{cjhebrew}")
        custom_template.add_to_preamble(r"\newcommand{\tav}{\text{\cjhebrew{t}}}")
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        pink_color = "#FF66B2"      
        purple_color = "#A468FF"
        brown_fill = "#4B3621"
        cyan_color = "#00FFFF"
        SCALE_FACTOR = 0.85

        # ----------------------------------------------------
        # t = 0.00s (9:08:17): Start Scene 16
        # Recreate exact Final Frame of Scene 15
        # ----------------------------------------------------
        
        new_lhs = MathTex(r"\vec{a}", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        new_lhs[0].set_color(pink_color)
        new_lhs[1].set_color(purple_color)
        
        new_rhs_app = MathTex(r"=", r"\vec{a}", r"\cdot", r"\vec{b}", r"+", r"\vec{a}", r"\wedge", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        new_rhs_app[1].set_color(pink_color)
        new_rhs_app[3].set_color(purple_color)
        new_rhs_app[5].set_color(pink_color)
        new_rhs_app[7].set_color(purple_color)

        final_eq = VGroup(new_lhs, new_rhs_app).arrange(RIGHT, buff=0.2)
        final_eq.move_to(UP * 1.5)
        self.add(final_eq)

        # ----------------------------------------------------
        # Assemble Fade Group (Bottom 3 lines from Scene 15)
        # ----------------------------------------------------
        fade_group = VGroup()

        bivec_y_pos = -2.8
        shift_left = LEFT * 4.2

        num_2 = MathTex("2").scale(1.0).move_to(LEFT * 1.5 + UP * 0.8).shift(shift_left)
        num_3 = MathTex("3").scale(1.0).move_to(RIGHT * 1.5 + UP * 0.8).shift(shift_left)
        plus_num = MathTex("+").scale(1.0).move_to((num_2.get_center() + num_3.get_center()) / 2)
        
        vec_x = Arrow(ORIGIN, RIGHT * 0.8 + UP * 0.8, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        vec_x.move_to(LEFT * 1.5 + DOWN * 0.6).shift(shift_left)
        lbl_x = MathTex(r"\vec{x}", tex_template=custom_template, color=purple_color).next_to(vec_x, LEFT, buff=0.15)
        
        vec_y = Arrow(ORIGIN, RIGHT * 1.1 + DOWN * 0.4, buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        vec_y.move_to(RIGHT * 1.5 + DOWN * 0.6).shift(shift_left)
        lbl_y = MathTex(r"\vec{y}", tex_template=custom_template, color=pink_color).next_to(vec_y, RIGHT, buff=0.15)
        
        plus_vec = MathTex("+").scale(1.0).move_to((vec_x.get_center() + vec_y.get_center()) / 2)

        target_pos = vec_x.get_center()

        c_A = np.array([-1.5, bivec_y_pos, 0]) + shift_left
        w_A, h_A = 1.6, 1.1
        A_TL = c_A + LEFT * w_A / 2 + UP * h_A / 2
        A_TR = c_A + RIGHT * w_A / 2 + UP * h_A / 2
        A_BR = c_A + RIGHT * w_A / 2 + DOWN * h_A / 2
        A_BL = c_A + LEFT * w_A / 2 + DOWN * h_A / 2

        area_A = Polygon(A_TL, A_TR, A_BR, A_BL, fill_opacity=0.4, stroke_width=0).set_fill(DARK_BLUE)
        arr_A1 = Arrow(A_TL, A_TR, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A2 = Arrow(A_TR, A_BR, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A3 = Arrow(A_BR, A_BL, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A4 = Arrow(A_BL, A_TL, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        lbl_A = MathTex(r"\bivec{A}", tex_template=custom_template, color=BLUE).next_to(area_A, LEFT, buff=0.25)

        c_B = np.array([1.5, bivec_y_pos, 0]) + shift_left
        w_B, h_B = 1.0, 1.1
        B_TL = c_B + LEFT * w_B / 2 + UP * h_B / 2
        B_TR = c_B + RIGHT * w_B / 2 + UP * h_B / 2
        B_BR = c_B + RIGHT * w_B / 2 + DOWN * h_B / 2
        B_BL = c_B + LEFT * w_B / 2 + DOWN * h_B / 2

        area_B = Polygon(B_TL, B_TR, B_BR, B_BL, fill_opacity=0.4, stroke_width=0).set_fill(DARK_BROWN)
        arr_B1 = Arrow(B_TL, B_TR, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B2 = Arrow(B_TR, B_BR, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B3 = Arrow(B_BR, B_BL, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B4 = Arrow(B_BL, B_TL, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        lbl_B = MathTex(r"\bivec{B}", tex_template=custom_template, color=RED).next_to(area_B, RIGHT, buff=0.25)

        plus_bivec = MathTex("+").scale(1.0).move_to(np.array([plus_vec.get_x(), bivec_y_pos, 0]))

        line_num = VGroup(num_2, plus_num, num_3)
        grp_x = VGroup(vec_x, lbl_x)
        grp_y = VGroup(vec_y, lbl_y)
        line_vec = VGroup(grp_x, plus_vec, grp_y)
        grp_A = VGroup(area_A, arr_A1, arr_A2, arr_A3, arr_A4, lbl_A)
        grp_B = VGroup(area_B, arr_B1, arr_B2, arr_B3, arr_B4, lbl_B)
        line_biv = VGroup(grp_A, plus_bivec, grp_B)

        max_x = max(line_num.get_right()[0], line_vec.get_right()[0], line_biv.get_right()[0])
        eq_x = max_x + 0.6

        eq_num = MathTex("=").scale(1.0).move_to(np.array([eq_x, num_2.get_y(), 0]))
        num_5_rhs = MathTex("5").scale(1.0).next_to(eq_num, RIGHT, buff=0.6)

        eq_vec = MathTex("=").scale(1.0).move_to(np.array([eq_x, plus_vec.get_y(), 0]))
        
        vec_sum_end_relative = (RIGHT * 0.8 + UP * 0.8) + (RIGHT * 1.1 + DOWN * 0.4)
        vec_sum_rhs = Arrow(ORIGIN, vec_sum_end_relative, buff=0, color=YELLOW, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        vec_sum_rhs.next_to(eq_vec, RIGHT, buff=0.6)
        vec_sum_rhs.set_y(eq_vec.get_y() - 0.2)
        lbl_sum_rhs = MathTex(r"\vec{x} + \vec{y}", tex_template=custom_template, color=YELLOW).next_to(vec_sum_rhs, RIGHT, buff=0.2)

        eq_biv = MathTex("=").scale(1.0).move_to(np.array([eq_x, plus_bivec.get_y(), 0]))
        RHS_start_x = eq_biv.get_right()[0] + 0.6
        
        AB_TL_rhs = np.array([RHS_start_x, bivec_y_pos + h_A/2, 0])
        AB_T_mid_rhs = AB_TL_rhs + RIGHT * w_A
        AB_TR_rhs = AB_T_mid_rhs + RIGHT * w_B
        AB_BR_rhs = AB_TR_rhs + DOWN * h_A
        AB_B_mid_rhs = AB_T_mid_rhs + DOWN * h_A
        AB_BL_rhs = AB_TL_rhs + DOWN * h_A

        area_A_rhs = Polygon(AB_TL_rhs, AB_T_mid_rhs, AB_B_mid_rhs, AB_BL_rhs, fill_opacity=0.4, stroke_width=0).set_fill(DARK_BLUE)
        area_B_rhs = Polygon(AB_T_mid_rhs, AB_TR_rhs, AB_BR_rhs, AB_B_mid_rhs, fill_opacity=0.4, stroke_width=0).set_fill(DARK_BROWN)
        arr_A1_rhs = Arrow(AB_TL_rhs, AB_T_mid_rhs, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B1_rhs = Arrow(AB_T_mid_rhs, AB_TR_rhs, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B2_rhs = Arrow(AB_TR_rhs, AB_BR_rhs, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_B3_rhs = Arrow(AB_BR_rhs, AB_B_mid_rhs, buff=0, color=RED, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A3_rhs = Arrow(AB_B_mid_rhs, AB_BL_rhs, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        arr_A4_rhs = Arrow(AB_BL_rhs, AB_TL_rhs, buff=0, color=BLUE, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)

        biv_sum_rhs = VGroup(area_A_rhs, area_B_rhs, arr_A1_rhs, arr_B1_rhs, arr_B2_rhs, arr_B3_rhs, arr_A3_rhs, arr_A4_rhs)
        lbl_AB_rhs = MathTex(r"\bivec{A} + \bivec{B}", tex_template=custom_template, color=WHITE).next_to(biv_sum_rhs, RIGHT, buff=0.3)

        fade_group.add(
            num_2, num_3, plus_num,
            vec_x, lbl_x, vec_y, lbl_y, plus_vec,
            area_A, arr_A1, arr_A2, arr_A3, arr_A4, lbl_A,
            area_B, arr_B1, arr_B2, arr_B3, arr_B4, lbl_B, plus_bivec,
            eq_num, num_5_rhs,
            eq_vec, vec_sum_rhs, lbl_sum_rhs,
            eq_biv, area_A_rhs, area_B_rhs, arr_A1_rhs, arr_B1_rhs, arr_B2_rhs, arr_B3_rhs, arr_A3_rhs, arr_A4_rhs, lbl_AB_rhs
        )
        self.add(fade_group)

        # ----------------------------------------------------
        # t = 8.99s (9:17:16): Duplicate a \cdot b and translate
        # ----------------------------------------------------
        self.wait(8.99)
        
        dot_term = new_rhs_app[1:4].copy()
        self.add(dot_term)
        
        self.play(
            FadeOut(fade_group),
            dot_term.animate.move_to(target_pos),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 9.99s: Draw a and b diagram to the right
        # ----------------------------------------------------
        diag_start = np.array([target_pos[0] + dot_term.width/2 + 1.2, target_pos[1] - 0.2, 0])
        
        a_x, a_y = 1.4 * 0.8, 1.9 * 0.8
        b_x = 2.7 * 0.8
        theta_0 = np.arctan2(a_y, a_x)
        dir_0 = np.array([np.cos(theta_0), np.sin(theta_0), 0])
        
        vec_a_diag = Arrow(diag_start, diag_start + RIGHT * a_x + UP * a_y, buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        vec_b_diag = Arrow(diag_start, diag_start + RIGHT * b_x, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        
        lbl_a_diag = MathTex(r"\vec{a}", tex_template=custom_template, color=pink_color).move_to(vec_a_diag.get_end() + dir_0 * 0.3)
        lbl_b_diag = MathTex(r"\vec{b}", tex_template=custom_template, color=purple_color).next_to(vec_b_diag.get_end(), DOWN, buff=0.15)
        
        self.play(
            GrowArrow(vec_b_diag),
            GrowArrow(vec_a_diag),
            Write(lbl_b_diag),
            Write(lbl_a_diag),
            run_time=0.78
        )

        # ----------------------------------------------------
        # t = 10.77s (9:19:03): Show shadow of a on b
        # ----------------------------------------------------
        proj_point = diag_start + RIGHT * a_x
        proj_line = DashedLine(vec_a_diag.get_end(), proj_point, color=GRAY)
        
        shadow_glow = create_hazy_line(
            start_pt=diag_start, 
            end_pt=proj_point, 
            color=pink_color, 
            core_width=0.05, 
            glow_radius=0.40, 
            num_layers=30, 
            opacity=1.0
        )

        self.play(
            FadeIn(proj_line),
            FadeIn(shadow_glow),
            run_time=1.5
        )

        diag1_group = VGroup(vec_a_diag, vec_b_diag, lbl_a_diag, lbl_b_diag, proj_line, shadow_glow)

        # ----------------------------------------------------
        # t = 12.73s (9:21:00): Duplicate a \wedge b and show diagram
        # ----------------------------------------------------
        self.wait(0.46)
        
        wedge_term = new_rhs_app[5:8].copy()
        self.add(wedge_term)
        
        wedge_target_x = target_pos[0] + 6.2  
        wedge_target_pos = np.array([wedge_target_x, target_pos[1], 0])
        
        diag_start_2 = np.array([wedge_target_x + wedge_term.width/2 + 1.2, target_pos[1] - 0.2, 0])
        
        vec_a_diag_2 = Arrow(diag_start_2, diag_start_2 + RIGHT * a_x + UP * a_y, buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        vec_b_diag_2 = Arrow(diag_start_2, diag_start_2 + RIGHT * b_x, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        
        lbl_a_diag_2 = MathTex(r"\vec{a}", tex_template=custom_template, color=pink_color).move_to(vec_a_diag_2.get_end() + dir_0 * 0.3)
        lbl_b_diag_2 = MathTex(r"\vec{b}", tex_template=custom_template, color=purple_color).next_to(vec_b_diag_2.get_end(), DOWN, buff=0.15)
        
        self.play(
            wedge_term.animate.move_to(wedge_target_pos),
            FadeIn(vec_a_diag_2),
            FadeIn(vec_b_diag_2),
            FadeIn(lbl_a_diag_2),
            FadeIn(lbl_b_diag_2),
            run_time=1.2
        )

        # ----------------------------------------------------
        # t = 13.93s (9:22:14): b translates up a, sweeping area
        # ----------------------------------------------------
        C0 = diag_start_2
        C1 = C0 + RIGHT * a_x + UP * a_y
        C3 = C0 + RIGHT * b_x
        C2 = C1 + RIGHT * b_x

        sweep_area = Polygon(C0, C1, C1, C0, fill_opacity=0.8, stroke_width=0).set_fill(brown_fill)
        sweep_area.set_z_index(-1)
        self.add(sweep_area)
        
        def update_sweep(mob, alpha):
            current_C1 = C0 + alpha * (C1 - C0)
            current_C2 = C3 + alpha * (C1 - C0)
            new_poly = Polygon(C0, current_C1, current_C2, C3, fill_opacity=0.8, stroke_width=0).set_fill(brown_fill)
            new_poly.set_z_index(-1)
            mob.become(new_poly)

        def custom_fade(mob, alpha):
            if alpha < 0.3:
                mob.set_opacity(0)
            else:
                mob.set_opacity((alpha - 0.3) / 0.7)

        vec_minus_a = Arrow(C2, C3, buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1).set_opacity(0)
        vec_minus_b = Arrow(C3, C0, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1).set_opacity(0)
        self.add(vec_minus_a, vec_minus_b)

        self.play(
            vec_b_diag_2.animate.shift(C1 - C0),
            lbl_b_diag_2.animate.next_to(C2, UP, buff=0.15),
            UpdateFromAlphaFunc(sweep_area, update_sweep),
            UpdateFromAlphaFunc(vec_minus_a, custom_fade),
            UpdateFromAlphaFunc(vec_minus_b, custom_fade),
            run_time=2.0
        )

        diag2_group = VGroup(vec_a_diag_2, vec_b_diag_2, lbl_a_diag_2, lbl_b_diag_2, sweep_area, vec_minus_a, vec_minus_b)

        # ----------------------------------------------------
        # t = 16.92s (9:25:13): Smooth slide & Blink Reset
        # ----------------------------------------------------
        self.wait(0.99)
        
        ab_term = MathTex(r"\vec{a}", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        ab_term[0].set_color(pink_color)
        ab_term[1].set_color(purple_color)
        ab_term.move_to(dot_term[0].get_left(), aligned_edge=LEFT)
        ab_term.set_y(dot_term.get_y())

        stop_pos_x = dot_term.get_right()[0] + wedge_term.width / 2 + 0.15
        stop_pos = np.array([stop_pos_x, target_pos[1], 0])

        self.play(
            FadeOut(diag2_group),
            run_time=0.3
        )
        
        self.play(
            wedge_term.animate(rate_func=linear).move_to(stop_pos),
            FadeOut(diag1_group, rate_func=lambda t: 0 if t < 0.7 else (t - 0.7) / 0.3),
            run_time=0.5
        )
        
        fresh_diag_start = diag_start
        
        A_radius = np.hypot(a_x, a_y)

        def get_projection_radius(angle):
            return max(A_radius * abs(np.cos(angle - theta_0)), 1e-4)

        center_dot = Dot(fresh_diag_start, radius=0).set_opacity(0)
        self.add(center_dot)
        
        fresh_vec_a = Arrow(fresh_diag_start, fresh_diag_start + RIGHT * a_x + UP * a_y, buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        fresh_vec_b = Arrow(fresh_diag_start, fresh_diag_start + RIGHT * b_x, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        
        fresh_lbl_a = MathTex(r"\vec{a}", tex_template=custom_template, color=pink_color).move_to(fresh_vec_a.get_end() + dir_0 * 0.3)
        fresh_lbl_b = MathTex(r"\vec{b}", tex_template=custom_template, color=purple_color).next_to(fresh_vec_b.get_end(), DOWN, buff=0.15)
        
        self.play(
            ReplacementTransform(VGroup(dot_term, wedge_term), ab_term),
            FadeIn(fresh_vec_a),
            FadeIn(fresh_vec_b),
            FadeIn(fresh_lbl_a),
            FadeIn(fresh_lbl_b),
            run_time=0.15
        )

        # ----------------------------------------------------
        # Target t = 19.85s: Start rendering circles
        # ----------------------------------------------------
        self.wait(1.98)
        
        circle1 = Circle(radius=A_radius / 2, color=pink_color, stroke_width=2)
        circle1.move_to(RIGHT * (A_radius / 2))
        
        circle2 = Circle(radius=A_radius / 2, color=pink_color, stroke_width=2)
        circle2.move_to(LEFT * (A_radius / 2))
        
        path_shape = VGroup(circle1, circle2)
        path_shape.rotate(theta_0, about_point=ORIGIN)
        path_shape.set_stroke(opacity=0.3).set_fill(opacity=0)
        path_shape.move_to(center_dot.get_center())

        line_para = Line(ORIGIN, RIGHT * a_x, color=pink_color, stroke_width=2).set_opacity(0.3)
        line_perp = Line(ORIGIN, UP * a_y, color=pink_color, stroke_width=2).set_opacity(0.3)
        
        line_para.shift(fresh_diag_start)
        line_perp.shift(fresh_diag_start)

        lbl_para = MathTex(r"a_{\parallel}", tex_template=custom_template, color=pink_color).scale(0.7).next_to(line_para, DOWN, buff=0.4).set_opacity(0.5)
        lbl_perp = MathTex(r"a_{\perp}", tex_template=custom_template, color=pink_color).scale(0.7).next_to(line_perp, LEFT, buff=0.6).set_opacity(0.5)
        
        self.play(
            FadeIn(path_shape), 
            FadeIn(line_para), 
            FadeIn(line_perp), 
            FadeIn(lbl_para), 
            FadeIn(lbl_perp), 
            run_time=1.0
        )

        self.wait(0.2)

        # ----------------------------------------------------
        # t = 22.96s: Continuous Translation & Rotation
        # ----------------------------------------------------
        angle_tracker = ValueTracker(theta_0)
        target_angle = theta_0 - 2.5 * PI
        total_shift = RIGHT * 14.4
        
        fade_start = -1.5 * PI - 0.1
        fade_end = -1.5 * PI - 0.6
        
        def get_opacity_for_angle(current_angle):
            if current_angle > fade_start:
                return 1.0
            elif current_angle < fade_end:
                return 0.0
            return (current_angle - fade_end) / (fade_start - fade_end)

        def is_flashing(current_angle):
            return (0 >= current_angle > -0.4) or (-1.5 * PI >= current_angle > -1.5 * PI - 0.4)

        def update_path(mob):
            mob.move_to(center_dot.get_center())
            angle = angle_tracker.get_value()
            mob.set_stroke(opacity=0.3 * get_opacity_for_angle(angle))

        def update_para(mob):
            start = center_dot.get_center()
            end = start + RIGHT * a_x
            mob.put_start_and_end_on(start, end)
            mob.set_stroke(opacity=0.3 * get_opacity_for_angle(angle_tracker.get_value()))
            
        def update_perp(mob):
            start = center_dot.get_center()
            end = start + UP * a_y
            mob.put_start_and_end_on(start, end)
            mob.set_stroke(opacity=0.3 * get_opacity_for_angle(angle_tracker.get_value()))
            
        def update_lbl_para(mob):
            mob.next_to(center_dot.get_center() + RIGHT * (a_x / 2), DOWN, buff=0.4)
            mob.set_opacity(0.5 * get_opacity_for_angle(angle_tracker.get_value()))
            
        def update_lbl_perp(mob):
            mob.next_to(center_dot.get_center() + UP * (a_y / 2), LEFT, buff=0.6)
            mob.set_opacity(0.5 * get_opacity_for_angle(angle_tracker.get_value()))

        def update_a(mob):
            angle = angle_tracker.get_value()
            r = get_projection_radius(angle)
            start_pt = center_dot.get_center()
            end_pt = start_pt + np.array([np.cos(angle), np.sin(angle), 0]) * r
            op = get_opacity_for_angle(angle)
            col = WHITE if is_flashing(angle) else pink_color
            mob.become(Arrow(start_pt, end_pt, buff=0, color=col, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1).set_opacity(op))

        def update_b(mob):
            angle = angle_tracker.get_value()
            start_pt = center_dot.get_center()
            end_pt = start_pt + RIGHT * b_x
            op = get_opacity_for_angle(angle)
            col = WHITE if is_flashing(angle) else purple_color
            mob.become(Arrow(start_pt, end_pt, buff=0, color=col, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1).set_opacity(op))

        def update_lbl_a(mob):
            angle = angle_tracker.get_value()
            r = get_projection_radius(angle)
            dir_vec = np.array([np.cos(angle), np.sin(angle), 0])
            end_pt = center_dot.get_center() + dir_vec * r
            mob.move_to(end_pt + dir_vec * 0.3)
            mob.set_opacity(get_opacity_for_angle(angle))

        def update_lbl_b(mob):
            angle = angle_tracker.get_value()
            mob.next_to(center_dot.get_center() + RIGHT * b_x, DOWN, buff=0.15)
            mob.set_opacity(get_opacity_for_angle(angle))

        val1 = theta_0 / (2.5 * PI)
        t1_alpha = (2 / PI) * np.arcsin(val1)
        val2 = (theta_0 + 1.5 * PI) / (2.5 * PI)
        t2_alpha = (2 / PI) * np.arcsin(val2)
        
        pos1_x = fresh_diag_start[0] + total_shift[0] * t1_alpha
        pos2_x = fresh_diag_start[0] + total_shift[0] * t2_alpha
        
        snap1_pos = fresh_diag_start + total_shift * t1_alpha
        snap2_pos = fresh_diag_start + total_shift * t2_alpha
        
        snap1_a = Arrow(snap1_pos, snap1_pos + RIGHT * get_projection_radius(0), buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1).set_opacity(0)
        snap1_b = Arrow(snap1_pos, snap1_pos + RIGHT * b_x, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1).set_opacity(0)
        
        snap2_a = Arrow(snap2_pos, snap2_pos + UP * get_projection_radius(-1.5 * PI), buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1).set_opacity(0)
        snap2_b = Arrow(snap2_pos, snap2_pos + RIGHT * b_x, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1).set_opacity(0)

        snap1_group = VGroup(snap1_a, snap1_b)
        snap2_group = VGroup(snap2_a, snap2_b)
        snap1_group.set_opacity(0)
        snap2_group.set_opacity(0)

        self.add(snap1_group, snap2_group)

        lbl_cos = MathTex(r"a", r"\cos \theta", r"\cdot", r"b", tex_template=custom_template).scale(0.65)
        lbl_cos[0].set_color(pink_color)
        lbl_cos[1].set_color(cyan_color)
        lbl_cos[3].set_color(purple_color)
        lbl_cos.next_to(snap1_b, DOWN, buff=0.15)
        lbl_cos.set_opacity(0)

        lbl_sin = MathTex(r"a", r"\sin \theta", r"\cdot", r"b", tex_template=custom_template).scale(0.65)
        lbl_sin[0].set_color(pink_color)
        lbl_sin[1].set_color(cyan_color)
        lbl_sin[3].set_color(purple_color)
        lbl_sin.next_to(snap2_b, DOWN, buff=0.15)
        lbl_sin.set_opacity(0)

        self.add(lbl_cos, lbl_sin)

        def update_snap1(mob):
            if angle_tracker.get_value() <= 0:
                mob.set_opacity(1)

        def update_lbl_cos(mob):
            val = angle_tracker.get_value()
            if val <= 0:
                op = np.clip((0 - val) / (0.3 * PI), 0.0, 1.0)
                mob.set_opacity(op)

        def update_snap2(mob):
            if angle_tracker.get_value() <= -1.5 * PI:
                mob.set_opacity(1)

        def update_lbl_sin(mob):
            val = angle_tracker.get_value()
            if val <= -1.5 * PI:
                op = np.clip((-1.5 * PI - val) / (0.3 * PI), 0.0, 1.0)
                mob.set_opacity(op)

        snap1_group.add_updater(update_snap1)
        lbl_cos.add_updater(update_lbl_cos)
        snap2_group.add_updater(update_snap2)
        lbl_sin.add_updater(update_lbl_sin)

        path_shape.add_updater(update_path)
        line_para.add_updater(update_para)
        line_perp.add_updater(update_perp)
        lbl_para.add_updater(update_lbl_para)
        lbl_perp.add_updater(update_lbl_perp)
        fresh_vec_a.add_updater(update_a)
        fresh_vec_b.add_updater(update_b)
        fresh_lbl_a.add_updater(update_lbl_a)
        fresh_lbl_b.add_updater(update_lbl_b)

        self.play(
            angle_tracker.animate(rate_func=rate_functions.ease_out_sine).set_value(target_angle),
            center_dot.animate(rate_func=linear).shift(total_shift),
            run_time=5.5
        )
        
        line_para.clear_updaters()
        line_perp.clear_updaters()
        lbl_para.clear_updaters()
        lbl_perp.clear_updaters()

        self.wait(0.38)

        # ----------------------------------------------------
        # Wave Superposition Graph Addition (Below ab term)
        # ----------------------------------------------------
        axes_base = Axes(
            x_range=[0, 2 * PI, PI / 2],
            y_range=[-2.5, 2.5, 1],
            x_length=3.0, 
            y_length=2.0,
            axis_config={"include_numbers": False}
        )
        
        alpha_c1 = 1.0 / 3.0
        alpha_c2 = 5.0 / 6.0

        D_frame = pos2_x - pos1_x
        total_curve_shift = RIGHT * (D_frame / (alpha_c2 - alpha_c1))
        
        X_start = pos1_x - (total_curve_shift[0] * alpha_c1)
        target_origin = np.array([X_start, target_pos[1] - 2.2, 0])
        axes_base.shift(target_origin - axes_base.coords_to_point(0, 0))

        f_func = lambda x: np.sin(x) + 0.4 * np.sin(3 * x)

        def get_c(alpha):
            slope = -PI / (alpha_c2 - alpha_c1)
            return PI + slope * (alpha - alpha_c1)

        def get_f_curve(alpha, op, col=purple_color):
            curve = axes_base.plot(f_func, x_range=[0, 2 * PI], color=col, stroke_width=3)
            curve.shift(total_curve_shift * alpha)
            curve.set_stroke(opacity=op)
            return curve

        def get_g_curve(alpha, op, col=pink_color):
            c = get_c(alpha)
            g_func_c = lambda x: 0.8 * np.sin(x - c) + 0.35 * np.sin(3 * (x - c))
            curve = axes_base.plot(g_func_c, x_range=[0, 2 * PI], color=col, stroke_width=3)
            curve.shift(total_curve_shift * alpha)
            curve.set_stroke(opacity=op)
            return curve
            
        def get_sum_curve(alpha, op, col=YELLOW):
            c = get_c(alpha)
            sum_func_c = lambda x: f_func(x) + 0.8 * np.sin(x - c) + 0.35 * np.sin(3 * (x - c))
            curve = axes_base.plot(sum_func_c, x_range=[0, 2 * PI], color=col, stroke_width=3)
            curve.shift(total_curve_shift * alpha)
            curve.set_stroke(opacity=op)
            return curve

        curve_f = get_f_curve(0, 1.0)
        curve_g = get_g_curve(0, 1.0)
        curve_sum = get_sum_curve(0, 1.0)

        self.play(
            Create(curve_f),
            Create(curve_g),
            Create(curve_sum),
            run_time=1.0
        )

        # ----------------------------------------------------
        # Superposition Translation & Phase Shift
        # ----------------------------------------------------
        curve_alpha_tracker = ValueTracker(0)

        curve_f_cpi = get_f_curve(alpha_c1, 0)
        curve_g_cpi = get_g_curve(alpha_c1, 0)
        curve_sum_cpi = get_sum_curve(alpha_c1, 0)
        
        curve_f_c0 = get_f_curve(alpha_c2, 0)
        curve_g_c0 = get_g_curve(alpha_c2, 0)
        curve_sum_c0 = get_sum_curve(alpha_c2, 0)

        self.add(curve_f_cpi, curve_g_cpi, curve_sum_cpi, curve_f_c0, curve_g_c0, curve_sum_c0)

        def get_curve_opacity(alpha):
            fade_start = 0.90
            fade_end = 1.00
            if alpha <= fade_start:
                return 1.0
            elif alpha >= fade_end:
                return 0.0
            else:
                return 1.0 - (alpha - fade_start) / (fade_end - fade_start)

        def is_curve_flashing(alpha):
            return (alpha_c1 <= alpha < alpha_c1 + 0.04) or (alpha_c2 <= alpha < alpha_c2 + 0.04)

        def update_curve_f(mob):
            alpha = curve_alpha_tracker.get_value()
            op = get_curve_opacity(alpha)
            col = WHITE if is_curve_flashing(alpha) else purple_color
            mob.become(get_f_curve(alpha, op, col))
            
        def update_curve_g(mob):
            alpha = curve_alpha_tracker.get_value()
            op = get_curve_opacity(alpha)
            col = WHITE if is_curve_flashing(alpha) else pink_color
            mob.become(get_g_curve(alpha, op, col))
            
        def update_curve_sum(mob):
            alpha = curve_alpha_tracker.get_value()
            op = get_curve_opacity(alpha)
            col = WHITE if is_curve_flashing(alpha) else YELLOW
            mob.become(get_sum_curve(alpha, op, col))

        def update_curve_freeze_cpi(mob):
            if curve_alpha_tracker.get_value() >= alpha_c1:
                curve_f_cpi.set_stroke(opacity=1.0)
                curve_g_cpi.set_stroke(opacity=1.0)
                curve_sum_cpi.set_stroke(opacity=1.0)

        def update_curve_freeze_c0(mob):
            if curve_alpha_tracker.get_value() >= alpha_c2:
                curve_f_c0.set_stroke(opacity=1.0)
                curve_g_c0.set_stroke(opacity=1.0)
                curve_sum_c0.set_stroke(opacity=1.0)

        curve_f.add_updater(update_curve_f)
        curve_g.add_updater(update_curve_g)
        curve_sum.add_updater(update_curve_sum)
        curve_f_cpi.add_updater(update_curve_freeze_cpi)
        curve_f_c0.add_updater(update_curve_freeze_c0)

        self.play(
            curve_alpha_tracker.animate(rate_func=linear).set_value(1.0),
            run_time=4.0
        )
        
        curve_f.clear_updaters()
        curve_g.clear_updaters()
        curve_sum.clear_updaters()

        self.wait(10.0)
        
        
        
        
class Scene17(Scene):
    def construct(self):
        custom_template = TexTemplate()
        custom_template.add_to_preamble(r"\usepackage{amssymb}")
        custom_template.add_to_preamble(r"\usepackage{graphicx}")
        custom_template.add_to_preamble(r"\usepackage{accents}")
        custom_template.add_to_preamble(r"\usepackage{cjhebrew}")
        custom_template.add_to_preamble(r"\newcommand{\tav}{\text{\cjhebrew{t}}}")
        custom_template.add_to_preamble(r"\newcommand*{\spinarrow}{\scalebox{0.7}[0.3]{$\circlearrowleft$}}")
        custom_template.add_to_preamble(r"\newcommand*{\bivec}[1]{\accentset{\spinarrow}{#1}}")

        pink_color = "#FF66B2"     
        purple_color = "#A468FF"
        brown_fill = "#4B3621"
        cyan_color = "#00FFFF"
        orange_fill = "#FFA500"
        SCALE_FACTOR = 0.85

        # ----------------------------------------------------
        # Recreate exact Final Frame of Scene 16
        # ----------------------------------------------------
        
        new_lhs = MathTex(r"\vec{a}", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        new_lhs[0].set_color(pink_color)
        new_lhs[1].set_color(purple_color)
        
        new_rhs_app = MathTex(r"=", r"\vec{a}", r"\cdot", r"\vec{b}", r"+", r"\vec{a}", r"\wedge", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        new_rhs_app[1].set_color(pink_color)
        new_rhs_app[3].set_color(purple_color)
        new_rhs_app[5].set_color(pink_color)
        new_rhs_app[7].set_color(purple_color)

        final_eq = VGroup(new_lhs, new_rhs_app).arrange(RIGHT, buff=0.2)
        final_eq.move_to(UP * 1.5)
        self.add(final_eq)

        # Silent layout calculation to achieve exact spatial match
        shift_left = LEFT * 4.2
        vec_x = Arrow(ORIGIN, RIGHT * 0.8 + UP * 0.8, buff=0).move_to(LEFT * 1.5 + DOWN * 0.6).shift(shift_left)
        target_pos = vec_x.get_center()

        dot_term = new_rhs_app[1:4].copy()
        dot_term.move_to(target_pos)

        # Restoring the ab term from Scene 16
        ab_term = MathTex(r"\vec{a}", r"\vec{b}", tex_template=custom_template).scale(SCALE_FACTOR)
        ab_term[0].set_color(pink_color)
        ab_term[1].set_color(purple_color)
        ab_term.move_to(dot_term[0].get_left(), aligned_edge=LEFT)
        ab_term.set_y(dot_term.get_y())
        self.add(ab_term)

        diag_start = np.array([target_pos[0] + dot_term.width/2 + 1.2, target_pos[1] - 0.2, 0])
        fresh_diag_start = diag_start
        
        a_x, a_y = 1.4 * 0.8, 1.9 * 0.8
        b_x = 2.7 * 0.8
        theta_0 = np.arctan2(a_y, a_x)
        dir_0 = np.array([np.cos(theta_0), np.sin(theta_0), 0])
        A_radius = np.hypot(a_x, a_y)

        def get_projection_radius(angle):
            return max(A_radius * abs(np.cos(angle - theta_0)), 1e-4)

        total_shift = RIGHT * 14.4
        val1 = theta_0 / (2.5 * PI)
        t1_alpha = (2 / PI) * np.arcsin(val1)
        val2 = (theta_0 + 1.5 * PI) / (2.5 * PI)
        t2_alpha = (2 / PI) * np.arcsin(val2)
        
        pos1_x = fresh_diag_start[0] + total_shift[0] * t1_alpha
        pos2_x = fresh_diag_start[0] + total_shift[0] * t2_alpha
        
        snap1_pos = fresh_diag_start + total_shift * t1_alpha
        snap2_pos = fresh_diag_start + total_shift * t2_alpha
        
        snap1_a = Arrow(snap1_pos, snap1_pos + RIGHT * get_projection_radius(0), buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        snap1_b = Arrow(snap1_pos, snap1_pos + RIGHT * b_x, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        
        snap2_a = Arrow(snap2_pos, snap2_pos + UP * get_projection_radius(-1.5 * PI), buff=0, color=pink_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)
        snap2_b = Arrow(snap2_pos, snap2_pos + RIGHT * b_x, buff=0, color=purple_color, stroke_width=4, tip_length=0.1875, max_tip_length_to_length_ratio=1)

        self.add(snap1_a, snap1_b, snap2_a, snap2_b)
        
        # Superposition Labels (Scaled 0.65, Cyan Trig)
        lbl_cos = MathTex(r"a", r"\cos \theta", r"\cdot", r"b", tex_template=custom_template).scale(0.65)
        lbl_cos[0].set_color(pink_color)
        lbl_cos[1].set_color(cyan_color)
        lbl_cos[3].set_color(purple_color)
        lbl_cos.next_to(snap1_b, DOWN, buff=0.15)

        lbl_sin = MathTex(r"a", r"\sin \theta", r"\cdot", r"b", tex_template=custom_template).scale(0.65)
        lbl_sin[0].set_color(pink_color)
        lbl_sin[1].set_color(cyan_color)
        lbl_sin[3].set_color(purple_color)
        lbl_sin.next_to(snap2_b, DOWN, buff=0.15)
        
        self.add(lbl_cos, lbl_sin)

        # Frozen Superposition Graphs
        axes_base = Axes(
            x_range=[0, 2 * PI, PI / 2],
            y_range=[-2.5, 2.5, 1],
            x_length=3.0, 
            y_length=2.0,
            axis_config={"include_numbers": False}
        )
        
        alpha_c1 = 1.0 / 3.0
        alpha_c2 = 5.0 / 6.0

        D_frame = pos2_x - pos1_x
        total_curve_shift = RIGHT * (D_frame / (alpha_c2 - alpha_c1))
        
        X_start = pos1_x - (total_curve_shift[0] * alpha_c1)
        target_origin = np.array([X_start, target_pos[1] - 2.2, 0])
        axes_base.shift(target_origin - axes_base.coords_to_point(0, 0))

        f_func = lambda x: np.sin(x) + 0.4 * np.sin(3 * x)

        def get_c(alpha):
            slope = -PI / (alpha_c2 - alpha_c1)
            return PI + slope * (alpha - alpha_c1)

        def get_f_curve(alpha, op, col=purple_color):
            curve = axes_base.plot(f_func, x_range=[0, 2 * PI], color=col, stroke_width=3)
            curve.shift(total_curve_shift * alpha)
            curve.set_stroke(opacity=op)
            return curve

        def get_g_curve(alpha, op, col=pink_color):
            c = get_c(alpha)
            g_func_c = lambda x: 0.8 * np.sin(x - c) + 0.35 * np.sin(3 * (x - c))
            curve = axes_base.plot(g_func_c, x_range=[0, 2 * PI], color=col, stroke_width=3)
            curve.shift(total_curve_shift * alpha)
            curve.set_stroke(opacity=op)
            return curve
            
        def get_sum_curve(alpha, op, col=YELLOW):
            c = get_c(alpha)
            sum_func_c = lambda x: f_func(x) + 0.8 * np.sin(x - c) + 0.35 * np.sin(3 * (x - c))
            curve = axes_base.plot(sum_func_c, x_range=[0, 2 * PI], color=col, stroke_width=3)
            curve.shift(total_curve_shift * alpha)
            curve.set_stroke(opacity=op)
            return curve

        curve_f_cpi = get_f_curve(alpha_c1, 1.0)
        curve_g_cpi = get_g_curve(alpha_c1, 1.0)
        curve_sum_cpi = get_sum_curve(alpha_c1, 1.0)
        
        curve_f_c0 = get_f_curve(alpha_c2, 1.0)
        curve_g_c0 = get_g_curve(alpha_c2, 1.0)
        curve_sum_c0 = get_sum_curve(alpha_c2, 1.0)

        self.add(curve_f_cpi, curve_g_cpi, curve_sum_cpi, curve_f_c0, curve_g_c0, curve_sum_c0)

        # ----------------------------------------------------
        # t = 1.00s (09:40:20): Ghost vector 'a' fades in with label
        # ----------------------------------------------------
        self.wait(1.0)
        
        ghost_a = Arrow(
            snap1_pos, snap1_pos + RIGHT * a_x + UP * a_y, 
            buff=0, color=pink_color, stroke_width=4, 
            tip_length=0.1875, max_tip_length_to_length_ratio=1
        ).set_opacity(0.4)
        
        lbl_ghost_a = MathTex(r"\vec{a}", tex_template=custom_template, color=pink_color).scale(0.65).set_opacity(0.4)
        lbl_ghost_a.move_to(ghost_a.get_end() + dir_0 * 0.3)
        
        self.play(FadeIn(ghost_a), FadeIn(lbl_ghost_a), run_time=0.5)

        # ----------------------------------------------------
        # t = 2.31s (09:41:38): Ghost vector 'a' collapses
        # ----------------------------------------------------
        self.wait(0.81)
        
        target_ghost_a = Arrow(
            snap1_pos, snap1_pos + RIGHT * get_projection_radius(0), 
            buff=0, color=pink_color, stroke_width=4, 
            tip_length=0.1875, max_tip_length_to_length_ratio=1
        ).set_opacity(0.4)
        
        lbl_ghost_a_para = MathTex(r"a", r"_{\parallel}", tex_template=custom_template).scale(0.65)
        lbl_ghost_a_para[0].set_color(pink_color)
        lbl_ghost_a_para[1].set_color(cyan_color)
        lbl_ghost_a_para.set_opacity(0.7)
        lbl_ghost_a_para.next_to(snap1_pos, LEFT, buff=0.15).shift(UP * 0.35)
        
        self.play(
            Transform(ghost_a, target_ghost_a), 
            Transform(lbl_ghost_a, lbl_ghost_a_para),
            run_time=0.8
        )
        self.remove(ghost_a)

        # ----------------------------------------------------
        # t = 3.40s: Append 'b' to a_para (Adjusted wait)
        # ----------------------------------------------------
        self.wait(0.29)
        
        lbl_cdot_b = MathTex(r"\cdot", r"b", tex_template=custom_template).scale(0.65)
        lbl_cdot_b[0].set_color(WHITE)
        lbl_cdot_b[1].set_color(purple_color)
        lbl_cdot_b.set_opacity(0.7)
        lbl_cdot_b.next_to(lbl_ghost_a_para, RIGHT, buff=0.1)
        lbl_cdot_b.set_y(lbl_ghost_a_para[0].get_y()) 
        
        self.play(FadeIn(lbl_cdot_b), run_time=0.5)

        # ----------------------------------------------------
        # t = 3.90s (09:43:14): Map vectors to Yin-Yang & fade in label
        # ----------------------------------------------------
        # No wait here so it lands precisely on the 3.90s mark
        
        yin_yang = VGroup()
        left_half = Arc(radius=0.5, start_angle=PI/2, angle=PI, fill_opacity=1, color=pink_color, stroke_width=0)
        right_half = Arc(radius=0.5, start_angle=-PI/2, angle=PI, fill_opacity=1, color=purple_color, stroke_width=0)
        top_circle = Circle(radius=0.25, fill_opacity=1, color=pink_color, stroke_width=0).shift(UP * 0.25)
        bottom_circle = Circle(radius=0.25, fill_opacity=1, color=purple_color, stroke_width=0).shift(DOWN * 0.25)
        
        yin_yang.add(left_half, right_half, top_circle, bottom_circle).scale(0.35 * 0.65)
        
        vectors_center_x = (snap1_pos[0] + (snap1_pos[0] + b_x)) / 2
        yin_yang.move_to(np.array([vectors_center_x, snap1_pos[1] + 0.75, 0]))
        
        dup_a = snap1_a.copy()
        dup_b = snap1_b.copy()
        self.add(dup_a, dup_b)

        lbl_dot_ball = MathTex(r"\vec{a}", r"\cdot", r"\vec{b}", tex_template=custom_template).scale(0.65)
        lbl_dot_ball[0].set_color(pink_color)
        lbl_dot_ball[1].set_color(WHITE)
        lbl_dot_ball[2].set_color(purple_color)
        lbl_dot_ball.next_to(yin_yang, UR, buff=0.1)
        
        self.play(
            ReplacementTransform(VGroup(dup_a, dup_b), yin_yang),
            FadeIn(lbl_dot_ball),
            run_time=1.0
        )

        # ----------------------------------------------------
        # t = 5.00s (09:44:20): Invisible Vertical Bar Eraser
        # ----------------------------------------------------
        self.wait(0.10)
        
        cover_rect = Rectangle(color=BLACK, fill_opacity=1, stroke_width=0)
        
        snap1_a.set_z_index(5)
        snap1_b.set_z_index(5)
        cover_rect.set_z_index(10)
        lbl_cos.set_z_index(15)
        lbl_ghost_a.set_z_index(15) 
        lbl_cdot_b.set_z_index(15) 
        yin_yang.set_z_index(15)
        lbl_dot_ball.set_z_index(15) 
        
        start_x = snap1_pos[0] + b_x + 0.2
        end_x = snap1_pos[0] - 0.3
        eraser_tracker = ValueTracker(start_x)
        
        def update_cover(mob):
            current_x = eraser_tracker.get_value()
            w = start_x - current_x
            mob.stretch_to_fit_width(max(w, 0.001))
            mob.stretch_to_fit_height(3.0) 
            mob.move_to(np.array([current_x + w / 2, snap1_pos[1], 0]))
            
        cover_rect.add_updater(update_cover)
        self.add(cover_rect)
        
        self.play(
            eraser_tracker.animate.set_value(end_x),
            run_time=1.5
        )
        
        cover_rect.clear_updaters()
        
        # ----------------------------------------------------
        # t = 7.60s (09:47:03): Ghost 'a' superimposes on right diagram
        # ----------------------------------------------------
        self.wait(1.10)
        
        ghost_a_2 = Arrow(
            snap2_pos, snap2_pos + RIGHT * a_x + UP * a_y, 
            buff=0, color=pink_color, stroke_width=4, 
            tip_length=0.1875, max_tip_length_to_length_ratio=1
        ).set_opacity(0.4)
        
        lbl_ghost_a_2 = MathTex(r"\vec{a}", tex_template=custom_template, color=pink_color).scale(0.65).set_opacity(0.4)
        lbl_ghost_a_2.move_to(ghost_a_2.get_end() + dir_0 * 0.3)
        
        self.play(FadeIn(ghost_a_2), FadeIn(lbl_ghost_a_2), run_time=0.5)

        # ----------------------------------------------------
        # t = 8.38s (09:48:23): Ghost vector 'a' collapses into vertical pink vector
        # ----------------------------------------------------
        self.wait(0.28)

        target_ghost_a_2 = Arrow(
            snap2_pos, snap2_pos + UP * get_projection_radius(-1.5 * PI), 
            buff=0, color=pink_color, stroke_width=4, 
            tip_length=0.1875, max_tip_length_to_length_ratio=1
        ).set_opacity(0.4)

        lbl_ghost_a_perp = MathTex(r"a", r"_{\perp}", tex_template=custom_template).scale(0.65)
        lbl_ghost_a_perp[0].set_color(pink_color)
        lbl_ghost_a_perp[1].set_color(cyan_color)
        lbl_ghost_a_perp.set_opacity(0.7)
        lbl_ghost_a_perp.next_to(target_ghost_a_2, LEFT, buff=0.6)

        self.play(
            Transform(ghost_a_2, target_ghost_a_2),
            Transform(lbl_ghost_a_2, lbl_ghost_a_perp),
            run_time=0.8
        )
        self.remove(ghost_a_2)

        # ----------------------------------------------------
        # t = 9.36s (09:49:22): Append '\cdot b' to a_perp
        # ----------------------------------------------------
        self.wait(0.18)

        lbl_cdot_b_2 = MathTex(r"\cdot", r"b", tex_template=custom_template).scale(0.65)
        lbl_cdot_b_2[0].set_color(WHITE)
        lbl_cdot_b_2[1].set_color(purple_color)
        lbl_cdot_b_2.set_opacity(0.7)
        lbl_cdot_b_2.next_to(lbl_ghost_a_perp, RIGHT, buff=0.1)
        lbl_cdot_b_2.set_y(lbl_ghost_a_perp[0].get_y()) 

        self.play(FadeIn(lbl_cdot_b_2), run_time=0.5)

        # ----------------------------------------------------
        # t = 10.15s (09:50:09): Slide purple vector up, orange filling
        # ----------------------------------------------------
        self.wait(0.28)

        rect_height = get_projection_radius(-1.5 * PI)
        rect_width = b_x

        filling_rect = Rectangle(
            width=rect_width, 
            height=0.001, 
            fill_color=orange_fill, 
            fill_opacity=0.5, 
            stroke_width=0
        )
        filling_rect.move_to(snap2_pos + RIGHT * (rect_width / 2) + UP * 0.0005)
        
        filling_rect.set_z_index(0)
        snap2_a.set_z_index(5)
        snap2_b.set_z_index(5)
        
        self.add(filling_rect)

        def update_filling(mob):
            current_y = snap2_b.get_start()[1]
            h = current_y - snap2_pos[1]
            if h < 0.001: 
                h = 0.001
            mob.stretch_to_fit_height(h)
            mob.move_to(snap2_pos + RIGHT * (rect_width / 2) + UP * (h / 2))
            
        filling_rect.add_updater(update_filling)

        self.play(
            snap2_b.animate.shift(UP * rect_height),
            run_time=0.75
        )
        filling_rect.clear_updaters()

        # ----------------------------------------------------
        # The remaining edges of the loop & Wedge b appear
        # ----------------------------------------------------
        neg_pink = Arrow(
            snap2_pos + RIGHT * rect_width + UP * rect_height, 
            snap2_pos + RIGHT * rect_width, 
            buff=0, color=pink_color, stroke_width=4, 
            tip_length=0.1875, max_tip_length_to_length_ratio=1
        ).set_z_index(5)

        neg_purple = Arrow(
            snap2_pos + RIGHT * rect_width, 
            snap2_pos, 
            buff=0, color=purple_color, stroke_width=4, 
            tip_length=0.1875, max_tip_length_to_length_ratio=1
        ).set_z_index(5)

        lbl_wedge = MathTex(r"\vec{a}", r"\wedge", r"\vec{b}", tex_template=custom_template).scale(0.85)
        lbl_wedge[0].set_color(pink_color)
        lbl_wedge[1].set_color(WHITE)
        lbl_wedge[2].set_color(purple_color)
        lbl_wedge.move_to(filling_rect.get_center())

        self.play(
            FadeIn(neg_pink), 
            FadeIn(neg_purple), 
            FadeIn(lbl_wedge),
            run_time=0.50
        )

        # ----------------------------------------------------
        # t = 17.13s (09:57:14): Bivector rotates to skewed 3D & everything else fades
        # ----------------------------------------------------
        self.wait(5.33)

        bivector_mobs = [filling_rect, snap2_a, snap2_b, neg_pink, neg_purple, lbl_wedge]
        everything_else = Group(*[m for m in self.mobjects if m not in bivector_mobs])
        bivector_group = VGroup(*bivector_mobs)

        self.play(
            FadeOut(everything_else),
            bivector_group.animate.move_to(DOWN * 1.2).rotate(30 * DEGREES, axis=OUT).rotate(70 * DEGREES, axis=RIGHT),
            run_time=2.0
        )

        # ----------------------------------------------------
        # t = 20.13s: Yellow vector c appears
        # ----------------------------------------------------
        self.wait(1.0)
        
        c_start = snap2_a.get_end() # Tip of a (top-left of the rotated bivector)
        
        # Determine the exact on-screen vectors for the bivector's edges post-rotation
        b_vec = snap2_b.get_end() - snap2_b.get_start()     # Purple direction
        neg_a_vec = snap2_a.get_start() - snap2_a.get_end() # Inward pink direction (-a)
        
        # Scale factor to shorten vector c while preserving its exact direction
        c_scale = 0.8
        
        # Project diagonally into the bivector, proportionally scaled
        c_proj_tip = c_start + b_vec * (0.85 * c_scale) + neg_a_vec * (0.35 * c_scale)
        
        # Complete vector C by lifting vertically from the projected tip, proportionally scaled
        c_end = c_proj_tip + UP * (1.2 * c_scale)
        
        vec_c = Arrow(
            c_start, c_end, 
            buff=0, color=YELLOW, stroke_width=4, 
            tip_length=0.1875, max_tip_length_to_length_ratio=1
        )
        
        lbl_c = MathTex(r"\vec{c}", tex_template=custom_template, color=YELLOW).scale(0.65)
        lbl_c.next_to(vec_c.get_end(), RIGHT, buff=0.1)

        self.play(FadeIn(vec_c), FadeIn(lbl_c), run_time=0.5)

        # ----------------------------------------------------
        # t = 22.00s (10:02:06): Vertical line and hazy shadow of c
        # ----------------------------------------------------
        self.wait(1.37)
        
        # The vertical line drops strictly straight down to visually intersect the 3D plane
        vert_line = Line(c_end, c_proj_tip, color=YELLOW, stroke_width=3).set_opacity(0.4)
        
        shadow_group = create_hazy_line(c_start, c_proj_tip, color=YELLOW)

        self.play(
            FadeIn(vert_line),
            FadeIn(shadow_group),
            run_time=0.8
        )

        # ----------------------------------------------------
        # Required 10.0 Second Tail
        # ----------------------------------------------------
        self.wait(10.0)
  


class Scene18(ThreeDScene):
    def construct(self):
        # Enforce deterministic generation
        random.seed(42)
        np.random.seed(42)
        
        # Match focal_distance with Scene19 to prevent perspective jolt
        self.set_camera_orientation(phi=0, theta=-PI/2, focal_distance=100.0)
        
        stars = VGroup()
        num_stars = 300 
        
        color_palette = [WHITE] * 20 + ["#E8F0FF", "#FFF0E8", "#FFFFF0"]
        
        for _ in range(num_stars):
            x = random.uniform(-10, 10)
            y = random.uniform(-6, 6)
            z = random.uniform(-30, 5)
            
            color = random.choice(color_palette)
            star = Dot(
                point=np.array([x, y, z]), 
                radius=random.uniform(0.015, 0.035), 
                color=color
            )
            star.initial_pos = star.get_center()
            stars.add(star)

        # Force the first 3 stars to align exactly with Scene19's hardcoded vectors
        vec_a_val = np.array([-1.4, 1.0, -2.3])
        vec_b_val = np.array([-2.1, -1.5, -1.5])
        vec_c_val = np.array([3.2, -0.2, -0.5])
        target_ends = [vec_a_val, vec_b_val, vec_c_val]
        
        for i, target in enumerate(target_ends):
            # Account for the 15 OUT offset applied during the move_anim
            stars[i].initial_pos = target - np.array([0, 0, 15])
            stars[i].move_to(stars[i].initial_pos)
            
        self.add(stars)
        
        # ----------------------------------------------------
        # 00:09:11 -> t = 9.18s
        # ----------------------------------------------------
        self.wait(9.18)
        
        # ----------------------------------------------------
        # Movement and Axes Creation (00:09:11 to 00:17:03)
        # ----------------------------------------------------
        move_duration = 7.87
        axes_delay = 14.30 - 9.18
        
        def move_stars_func(m, t):
            offset = 15 * rate_functions.ease_in_out_sine(t)
            for s in m:
                s.move_to(s.initial_pos + OUT * offset)

        move_anim = UpdateFromAlphaFunc(stars, move_stars_func, run_time=move_duration)
        
        axis_opacity = 0.3
        axis_y = Line(DOWN * 20, UP * 20, color=WHITE, stroke_opacity=axis_opacity)
        axis_1 = Line(LEFT * 20 + DOWN * 6, RIGHT * 20 + UP * 6, color=WHITE, stroke_opacity=axis_opacity)
        axis_2 = Line(LEFT * 20 + UP * 6, RIGHT * 20 + DOWN * 6, color=WHITE, stroke_opacity=axis_opacity)
        axes = VGroup(axis_y, axis_1, axis_2)
        
        axes_anim = FadeIn(axes, run_time=2.0)
        
        self.play(
            AnimationGroup(
                move_anim,
                axes_anim,
                lag_ratio=axes_delay / move_duration
            )
        )
        
        # ----------------------------------------------------
        # 00:17:03 -> t = 17.05s: Arrow Growth
        # ----------------------------------------------------
        # Directly use the pre-aligned target stars
        chosen_stars = [stars[0], stars[1], stars[2]]
        
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"
        
        arrow_colors = [PINK_COLOR, PURPLE_COLOR, BLUE_COLOR]
        arrows = VGroup()
        arrow_anims = []
        vec_labels = VGroup()
        label_anims = []
        
        for i, star in enumerate(chosen_stars):
            end_pos = star.get_center()
            
            arrow = CameraFacingArrow(
                start=ORIGIN, 
                end=ORIGIN, 
                color=arrow_colors[i], 
                tip_length=0.35, 
                camera_dir=OUT
            )
            arrows.add(arrow)
            
            def get_grow_updater(target_end):
                def updater(mob, alpha):
                    safe_alpha = max(alpha, 1e-4) 
                    current_end = ORIGIN + safe_alpha * (target_end - ORIGIN)
                    mob.set_start_and_end(ORIGIN, current_end)
                return updater
                
            arrow_anim = UpdateFromAlphaFunc(
                arrow, 
                get_grow_updater(end_pos), 
                run_time=1.2, 
                rate_func=rate_functions.ease_in_out_sine
            )
            arrow_anims.append(arrow_anim)
            
            x, y, z = end_pos
            vec_label = MathTex(
                r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (x, y, z)
            ).scale(0.6).set_color(arrow_colors[i])
            
            dir_2d = np.array([x, y, 0])
            if np.linalg.norm(dir_2d) > 0:
                dir_2d = dir_2d / np.linalg.norm(dir_2d)
            else:
                dir_2d = RIGHT
                
            vec_label.next_to(end_pos, dir_2d, buff=0.2)
            vec_labels.add(vec_label)
            
            label_anim = Write(vec_label, run_time=1.2)
            label_anims.append(label_anim)
            
        self.play(*arrow_anims)
        
        # ----------------------------------------------------
        # 00:19:02 -> t = 19.03s: Column Vectors
        # ----------------------------------------------------
        # Current time is 17.05s + 1.2s = 18.25s
        self.wait(19.03 - 18.25)
        
        self.play(*label_anims)
        
        # ----------------------------------------------------
        # 00:27:10 -> t = 27.17s: Zoom Out & Vector Labels
        # ----------------------------------------------------
        # Current time is 19.03s + 1.2s = 20.23s
        self.wait(27.17 - 20.23)
        
        vector_names = [r"\vec{a}", r"\vec{b}", r"\vec{c}"]
        name_labels = VGroup()
        name_anims = []
        
        for i, star in enumerate(chosen_stars):
            end_pos = star.get_center()
            mid = end_pos / 2
            
            d = end_pos
            dir_2d = np.array([-d[1], d[0], 0])
            if np.linalg.norm(dir_2d) > 1e-4:
                dir_2d = dir_2d / np.linalg.norm(dir_2d)
            else:
                dir_2d = UP
                
            name_label = MathTex(vector_names[i]).set_color(arrow_colors[i]).scale(0.9)
            name_label.move_to(mid + dir_2d * 0.35)
            name_labels.add(name_label)
            
            name_anims.append(Write(name_label, run_time=1.5))
            
        self.move_camera(
            zoom=0.66, 
            added_anims=[FadeOut(stars, run_time=1.5)] + name_anims, 
            run_time=2.0
        )
        
        # ----------------------------------------------------
        # Video-Editing Tail
        # ----------------------------------------------------
        self.wait(10.0)
        
        
        
class Scene19(ThreeDScene):
    def construct(self):
        # ----------------------------------------------------
        # Static Recreation of Scene 18 Final Frame
        # ----------------------------------------------------
        self.set_camera_orientation(phi=0, theta=-PI/2, zoom=0.66, focal_distance=100.0)
        
        # Axes
        axis_opacity = 0.3
        axis_y = Line(DOWN * 20, UP * 20, color=WHITE, stroke_opacity=axis_opacity)
        axis_1 = Line(LEFT * 20 + DOWN * 6, RIGHT * 20 + UP * 6, color=WHITE, stroke_opacity=axis_opacity)
        axis_2 = Line(LEFT * 20 + UP * 6, RIGHT * 20 + DOWN * 6, color=WHITE, stroke_opacity=axis_opacity)
        axes = VGroup(axis_y, axis_1, axis_2)
        self.add(axes)
        
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"
        SUM_COLOR = "#FFD700"
        
        vec_a_val = np.array([-1.4, 1.0, -2.3])
        vec_b_val = np.array([-2.1, -1.5, -1.5])
        vec_c_val = np.array([3.2, -0.2, -0.5])
        
        vectors = [
            (vec_a_val, PINK_COLOR, r"\vec{a}"),
            (vec_b_val, PURPLE_COLOR, r"\vec{b}"),
            (vec_c_val, BLUE_COLOR, r"\vec{c}")
        ]
        
        for pos, color, name in vectors:
            arrow = CameraFacingArrow(
                start=ORIGIN, 
                end=pos, 
                color=color, 
                tip_length=0.35, 
                camera_dir=OUT
            )
            self.add(arrow)
            
            x, y, z = pos
            vec_label = MathTex(
                r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (x, y, z)
            ).scale(0.6).set_color(color)
            
            dir_2d = np.array([x, y, 0])
            if np.linalg.norm(dir_2d) > 0:
                dir_2d = dir_2d / np.linalg.norm(dir_2d)
            else:
                dir_2d = RIGHT
                
            vec_label.next_to(pos, dir_2d, buff=0.2)
            self.add(vec_label)
            
            mid = pos / 2
            dir_2d_name = np.array([-pos[1], pos[0], 0])
            if np.linalg.norm(dir_2d_name) > 1e-4:
                dir_2d_name = dir_2d_name / np.linalg.norm(dir_2d_name)
            else:
                dir_2d_name = UP
                
            name_label = MathTex(name).set_color(color).scale(0.9)
            name_label.move_to(mid + dir_2d_name * 0.35)
            self.add(name_label)

        # ----------------------------------------------------
        # Scene 19 Start (00:28:18 -> t = 28.30s)
        # ----------------------------------------------------
        
        a_x, a_y, a_z = vec_a_val
        b_x, b_y, b_z = vec_b_val
        sum_vec_val = vec_a_val + vec_b_val
        sum_x, sum_y, sum_z = sum_vec_val
        
        # Construct Part 1: a + b = stack_a + stack_b
        vec_a_text = MathTex(r"\vec{a}").set_color(PINK_COLOR)
        plus_sign1 = MathTex("+")
        vec_b_text = MathTex(r"\vec{b}").set_color(PURPLE_COLOR)
        eq_sign1 = MathTex("=")
        
        stack_a = MathTex(r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (a_x, a_y, a_z)).set_color(PINK_COLOR)
        plus_sign2 = MathTex("+")
        stack_b = MathTex(r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (b_x, b_y, b_z)).set_color(PURPLE_COLOR)
        
        formula_part1 = VGroup(
            vec_a_text, plus_sign1, vec_b_text, eq_sign1, 
            stack_a, plus_sign2, stack_b
        ).arrange(RIGHT, buff=0.2).scale(0.8)
        
        formula_part1.move_to(RIGHT * 5.5 + UP * 4.5)
        
        # Construct Part 2: = stack_{a+b}
        eq_sign2 = MathTex("=")
        stack_sum = MathTex(r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (sum_x, sum_y, sum_z)).set_color(SUM_COLOR)
        
        formula_part2 = VGroup(eq_sign2, stack_sum).arrange(RIGHT, buff=0.2).scale(0.8)
        formula_part2.next_to(formula_part1, RIGHT, buff=0.2)
        
        # ----------------------------------------------------
        # Event 1: Extended pause for replaced audio (+20.4167s)
        # Old audio clip: 00:30:10 to 00:35:09 = 299 frames = 4.9833s
        # New audio clip: 00:30:10 to 00:55:34 = 1524 frames = 25.4000s
        # Additional pause: 1225 / 60 s = 20.4167s
        # ----------------------------------------------------
        audio_delay = 1225 / 60
        wait_1 = (35.00 - 28.30) + audio_delay
        self.wait(wait_1)
        
        anim_1_duration = 1.5
        self.play(Write(formula_part1), run_time=anim_1_duration)
        
        # ----------------------------------------------------
        # Event 2: 00:37:22 -> t = 37.37s (relative timing maintained)
        # ----------------------------------------------------
        wait_2 = 37.37 - (35.00 + anim_1_duration)
        self.wait(wait_2)
        
        anim_2_duration = 1.0
        self.play(Write(formula_part2), run_time=anim_2_duration)
        
        # ----------------------------------------------------
        # Event 3: 00:43:21 -> t = 43.35s (relative timing maintained)
        # ----------------------------------------------------
        wait_3 = 43.35 - (37.37 + anim_2_duration)
        self.wait(wait_3)
        
        top_left_origin = LEFT * 5.0 + UP * 2.5
        b_init_start = top_left_origin + LEFT * 2.2 + UP * 1.2
        
        dup_a = CameraFacingArrow(
            start=top_left_origin, 
            end=top_left_origin + vec_a_val, 
            color=PINK_COLOR, 
            tip_length=0.35, 
            camera_dir=OUT
        )
        
        dup_b = CameraFacingArrow(
            start=b_init_start, 
            end=b_init_start + vec_b_val, 
            color=PURPLE_COLOR, 
            tip_length=0.35, 
            camera_dir=OUT
        )
        
        anim_3_duration = 1.0
        self.play(FadeIn(dup_a), FadeIn(dup_b), run_time=anim_3_duration)
        
        # ----------------------------------------------------
        # Event 4: 00:45:03 -> t = 45.05s (relative timing maintained)
        # ----------------------------------------------------
        wait_4 = 45.05 - (43.35 + anim_3_duration)
        self.wait(max(wait_4, 0))
        
        start_b_initial = b_init_start
        end_b_initial = b_init_start + vec_b_val
        start_b_target = top_left_origin + vec_a_val
        end_b_target = start_b_target + vec_b_val
        
        def move_b_updater(mob, alpha):
            current_start = start_b_initial + alpha * (start_b_target - start_b_initial)
            current_end = end_b_initial + alpha * (end_b_target - end_b_initial)
            mob.set_start_and_end(current_start, current_end)
            
        anim_4a_duration = 0.8
        self.play(
            UpdateFromAlphaFunc(dup_b, move_b_updater),
            run_time=anim_4a_duration,
            rate_func=rate_functions.ease_in_out_sine
        )
            
        sum_vec_top = CameraFacingArrow(
            start=top_left_origin, 
            end=top_left_origin, 
            color=SUM_COLOR, 
            tip_length=0.35, 
            camera_dir=OUT
        )
        self.add(sum_vec_top)
        
        def grow_top_updater(mob, alpha):
            safe_alpha = max(alpha, 1e-4)
            mob.set_start_and_end(top_left_origin, top_left_origin + safe_alpha * sum_vec_val)
            
        sum_vec_origin = CameraFacingArrow(
            start=ORIGIN, 
            end=ORIGIN, 
            color=SUM_COLOR, 
            tip_length=0.35, 
            camera_dir=OUT
        )
        self.add(sum_vec_origin)
        
        def grow_origin_updater(mob, alpha):
            safe_alpha = max(alpha, 1e-4)
            mob.set_start_and_end(ORIGIN, safe_alpha * sum_vec_val)
            
        anim_4b_duration = 2.0
        self.play(
            UpdateFromAlphaFunc(sum_vec_top, grow_top_updater),
            UpdateFromAlphaFunc(sum_vec_origin, grow_origin_updater),
            run_time=anim_4b_duration,
            rate_func=rate_functions.ease_in_out_sine
        )
        
        # ----------------------------------------------------
        # Event 5: 00:49:18 -> t = 49.30s (relative timing maintained)
        # ----------------------------------------------------
        wait_5 = 49.30 - (45.05 + anim_4a_duration + anim_4b_duration)
        self.wait(max(wait_5, 0))
        
        stack_sum_dup = stack_sum.copy()
        
        dir_2d_sum = np.array([sum_x, sum_y, 0])
        if np.linalg.norm(dir_2d_sum) > 0:
            dir_2d_sum = dir_2d_sum / np.linalg.norm(dir_2d_sum)
        else:
            dir_2d_sum = RIGHT
            
        stack_target_pos = sum_vec_val + dir_2d_sum * 0.7
        
        mid_sum = sum_vec_val / 2
        dir_2d_name_sum = np.array([-sum_vec_val[1], sum_vec_val[0], 0])
        if np.linalg.norm(dir_2d_name_sum) > 1e-4:
            dir_2d_name_sum = dir_2d_name_sum / np.linalg.norm(dir_2d_name_sum)
        else:
            dir_2d_name_sum = UP
            
        sum_label = MathTex(r"\vec{a} + \vec{b}").set_color(SUM_COLOR).scale(0.9)
        sum_label.move_to(mid_sum + dir_2d_name_sum * 0.35)
        
        anim_5_duration = 1.5
        self.play(
            stack_sum_dup.animate.move_to(stack_target_pos),
            Write(sum_label),
            run_time=anim_5_duration
        )
        
        # ----------------------------------------------------
        # Video-Editing Tail
        # ----------------------------------------------------
        self.wait(10.0)
        
        

class Scene20(ThreeDScene):
    def construct(self):
        # ----------------------------------------------------
        # Static Recreation of Scene 19 Final Frame
        # ----------------------------------------------------
        self.set_camera_orientation(phi=0, theta=-PI/2, zoom=0.66, focal_distance=100.0)
        
        # Axes
        axis_opacity = 0.3
        axis_y = Line(DOWN * 20, UP * 20, color=WHITE, stroke_opacity=axis_opacity)
        axis_1 = Line(LEFT * 20 + DOWN * 6, RIGHT * 20 + UP * 6, color=WHITE, stroke_opacity=axis_opacity)
        axis_2 = Line(LEFT * 20 + UP * 6, RIGHT * 20 + DOWN * 6, color=WHITE, stroke_opacity=axis_opacity)
        axes = VGroup(axis_y, axis_1, axis_2)
        self.add(axes)
        
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"
        SUM_COLOR = "#FFD700"
        
        vec_a_val = np.array([-1.4, 1.0, -2.3])
        vec_b_val = np.array([-2.1, -1.5, -1.5])
        vec_c_val = np.array([3.2, -0.2, -0.5])
        sum_vec_val = vec_a_val + vec_b_val
        
        vectors = [
            (vec_a_val, PINK_COLOR, r"\vec{a}"),
            (vec_b_val, PURPLE_COLOR, r"\vec{b}"),
            (vec_c_val, BLUE_COLOR, r"\vec{c}")
        ]
        
        vec_a_label_mob = None 
        vec_a_arrow_mob = None
        vec_a_name_mob = None
        
        for pos, color, name in vectors:
            arrow = CameraFacingArrow(
                start=ORIGIN, 
                end=pos, 
                color=color, 
                tip_length=0.35, 
                camera_dir=OUT
            )
            self.add(arrow)
            
            x, y, z = pos
            vec_label = MathTex(
                r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (x, y, z)
            ).scale(0.6).set_color(color)
            
            dir_2d = np.array([x, y, 0])
            if np.linalg.norm(dir_2d) > 0:
                dir_2d = dir_2d / np.linalg.norm(dir_2d)
            else:
                dir_2d = RIGHT
                
            vec_label.next_to(pos, dir_2d, buff=0.2)
            self.add(vec_label)
            
            if name == r"\vec{a}":
                vec_a_label_mob = vec_label
                vec_a_arrow_mob = arrow
            
            mid = pos / 2
            dir_2d_name = np.array([-pos[1], pos[0], 0])
            if np.linalg.norm(dir_2d_name) > 1e-4:
                dir_2d_name = dir_2d_name / np.linalg.norm(dir_2d_name)
            else:
                dir_2d_name = UP
                
            name_label = MathTex(name).set_color(color).scale(0.9)
            name_label.move_to(mid + dir_2d_name * 0.35)
            self.add(name_label)
            
            if name == r"\vec{a}":
                vec_a_name_mob = name_label

        a_x, a_y, a_z = vec_a_val
        b_x, b_y, b_z = vec_b_val
        sum_x, sum_y, sum_z = sum_vec_val
        
        vec_a_text = MathTex(r"\vec{a}").set_color(PINK_COLOR)
        plus_sign1 = MathTex("+")
        vec_b_text = MathTex(r"\vec{b}").set_color(PURPLE_COLOR)
        eq_sign1 = MathTex("=")
        stack_a = MathTex(r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (a_x, a_y, a_z)).set_color(PINK_COLOR)
        plus_sign2 = MathTex("+")
        stack_b = MathTex(r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (b_x, b_y, b_z)).set_color(PURPLE_COLOR)
        
        formula_part1 = VGroup(
            vec_a_text, plus_sign1, vec_b_text, eq_sign1, 
            stack_a, plus_sign2, stack_b
        ).arrange(RIGHT, buff=0.2).scale(0.8)
        formula_part1.move_to(RIGHT * 5.5 + UP * 4.5)
        
        eq_sign2 = MathTex("=")
        stack_sum = MathTex(r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (sum_x, sum_y, sum_z)).set_color(SUM_COLOR)
        formula_part2 = VGroup(eq_sign2, stack_sum).arrange(RIGHT, buff=0.2).scale(0.8)
        formula_part2.next_to(formula_part1, RIGHT, buff=0.2)
        
        self.add(formula_part1, formula_part2)

        top_left_origin = LEFT * 5.0 + UP * 2.5
        
        dup_a = CameraFacingArrow(
            start=top_left_origin, 
            end=top_left_origin + vec_a_val, 
            color=PINK_COLOR, 
            tip_length=0.35, 
            camera_dir=OUT
        )
        dup_b = CameraFacingArrow(
            start=top_left_origin + vec_a_val, 
            end=top_left_origin + vec_a_val + vec_b_val, 
            color=PURPLE_COLOR, 
            tip_length=0.35, 
            camera_dir=OUT
        )
        sum_vec_top = CameraFacingArrow(
            start=top_left_origin, 
            end=top_left_origin + sum_vec_val, 
            color=SUM_COLOR, 
            tip_length=0.35, 
            camera_dir=OUT
        )
        
        self.add(dup_a, dup_b, sum_vec_top)

        sum_vec_origin = CameraFacingArrow(
            start=ORIGIN, 
            end=sum_vec_val, 
            color=SUM_COLOR, 
            tip_length=0.35, 
            camera_dir=OUT
        )
        self.add(sum_vec_origin)
        
        stack_sum_dup = stack_sum.copy()
        dir_2d_sum = np.array([sum_x, sum_y, 0])
        if np.linalg.norm(dir_2d_sum) > 0:
            dir_2d_sum = dir_2d_sum / np.linalg.norm(dir_2d_sum)
        else:
            dir_2d_sum = RIGHT
        stack_target_pos = sum_vec_val + dir_2d_sum * 0.7
        stack_sum_dup.move_to(stack_target_pos)
        
        mid_sum = sum_vec_val / 2
        dir_2d_name_sum = np.array([-sum_vec_val[1], sum_vec_val[0], 0])
        if np.linalg.norm(dir_2d_name_sum) > 1e-4:
            dir_2d_name_sum = dir_2d_name_sum / np.linalg.norm(dir_2d_name_sum)
        else:
            dir_2d_name_sum = UP
        sum_label = MathTex(r"\vec{a} + \vec{b}").set_color(SUM_COLOR).scale(0.9)
        sum_label.move_to(mid_sum + dir_2d_name_sum * 0.35)
        
        self.add(stack_sum_dup, sum_label)

        # ----------------------------------------------------
        # Scene 20 Start (00:51:12 -> t = 51.20s)
        # ----------------------------------------------------
        
        # ----------------------------------------------------
        # Event 1: 00:55:22 -> t = 55.37s
        # ----------------------------------------------------
        wait_1 = 55.37 - 51.20
        self.wait(wait_1)
        
        target_vec_val = 2 * vec_a_val
        
        target_sum_label = MathTex(r"\vec{a} + \vec{a}").set_color(SUM_COLOR).scale(0.9)
        mid_target = target_vec_val / 2
        
        dir_2d_name_target = np.array([target_vec_val[1], -target_vec_val[0], 0])
        if np.linalg.norm(dir_2d_name_target) > 1e-4:
            dir_2d_name_target = dir_2d_name_target / np.linalg.norm(dir_2d_name_target)
        else:
            dir_2d_name_target = UP
            
        target_sum_label.move_to(mid_target + dir_2d_name_target * 0.7)
        
        target_stack = MathTex(
            r"\begin{bmatrix} 2 \cdot -1.4 \\ 2 \cdot 1.0 \\ 2 \cdot -2.3 \end{bmatrix}"
        ).set_color(SUM_COLOR).scale(0.8)
        
        target_stack_pos = target_vec_val + LEFT * 1.5 + UP * 0.8
        target_stack.move_to(target_stack_pos)
        
        def sum_vec_updater(mob, alpha):
            current_end = sum_vec_val + alpha * (target_vec_val - sum_vec_val)
            mob.set_start_and_end(ORIGIN, current_end)
            
        anim_duration = 2.0
        safe_a_label_pos = vec_a_val + RIGHT * 1.5 + DOWN * 0.5
        
        self.play(
            UpdateFromAlphaFunc(sum_vec_origin, sum_vec_updater),
            Transform(sum_label, target_sum_label),
            Transform(stack_sum_dup, target_stack),
            vec_a_label_mob.animate.move_to(safe_a_label_pos),
            FadeOut(dup_a),
            FadeOut(dup_b),
            FadeOut(sum_vec_top),
            FadeOut(formula_part1),
            FadeOut(formula_part2),
            run_time=anim_duration
        )

        # ----------------------------------------------------
        # Event 2: 00:57:14 -> t = 57.23s
        # ----------------------------------------------------
        wait_2 = max(0, 57.23 - (55.37 + anim_duration))
        if wait_2 > 0:
            self.wait(wait_2)
            
        target_vec_val_3 = 3 * vec_a_val
        
        target_sum_label_3 = MathTex(r"3\vec{a}").set_color(SUM_COLOR).scale(0.9)
        mid_target_3 = target_vec_val_3 / 2
        
        dir_2d_name_target_3 = np.array([target_vec_val_3[1], -target_vec_val_3[0], 0])
        if np.linalg.norm(dir_2d_name_target_3) > 1e-4:
            dir_2d_name_target_3 = dir_2d_name_target_3 / np.linalg.norm(dir_2d_name_target_3)
        else:
            dir_2d_name_target_3 = UP
            
        target_sum_label_3.move_to(mid_target_3 + dir_2d_name_target_3 * 0.7)
        
        target_stack_3 = MathTex(
            r"\begin{bmatrix} 3 \cdot -1.4 \\ 3 \cdot 1.0 \\ 3 \cdot -2.3 \end{bmatrix}"
        ).set_color(SUM_COLOR).scale(0.8)
        
        target_stack_pos_3 = target_vec_val_3 + LEFT * 1.5 + UP * 0.8
        target_stack_3.move_to(target_stack_pos_3)
        
        def sum_vec_updater_3(mob, alpha):
            current_end = target_vec_val + alpha * (target_vec_val_3 - target_vec_val)
            mob.set_start_and_end(ORIGIN, current_end)
            
        anim_duration_3 = 2.0
        
        self.play(
            UpdateFromAlphaFunc(sum_vec_origin, sum_vec_updater_3),
            Transform(sum_label, target_sum_label_3),
            Transform(stack_sum_dup, target_stack_3),
            run_time=anim_duration_3
        )

        # ----------------------------------------------------
        # Event 3: 01:01:10 -> t = 61.17s
        # ----------------------------------------------------
        wait_3 = max(0, 61.17 - (57.23 + anim_duration_3))
        if wait_3 > 0:
            self.wait(wait_3)

        k_tracker = ValueTracker(3.0)

        def update_vector_k(mob):
            k = k_tracker.get_value()
            
            # Guard against exactly zero length which breaks arrow tip orientation
            if abs(k) < 1e-4:
                k = 1e-4 if k >= 0 else -1e-4
                
            # Using mob.become() forces a clean recreation of the arrow geometry
            # on every frame, eliminating snapping/floating artifacts on the 180 flip
            safe_arrow = CameraFacingArrow(
                start=ORIGIN, 
                end=k * vec_a_val, 
                color=SUM_COLOR, 
                tip_length=0.35, 
                camera_dir=OUT
            )
            mob.become(safe_arrow)

        def update_label_k(mob):
            k = k_tracker.get_value()
            
            k_str = f"{k:.1f}"
            if k_str.endswith(".0"):
                k_str = k_str[:-2]
            
            if k_str == "-0":
                k_str = "0"
            elif k_str == "1":
                k_str = ""
            elif k_str == "-1":
                k_str = "-"
                
            new_label = MathTex(r"%s\vec{a}" % k_str).set_color(SUM_COLOR).scale(0.9)
            vec_val = k * vec_a_val
            mid = vec_val / 2
            
            dir_2d_name = np.array([vec_val[1], -vec_val[0], 0])
            if np.linalg.norm(dir_2d_name) > 1e-4:
                dir_2d_name = dir_2d_name / np.linalg.norm(dir_2d_name)
            else:
                dir_2d_name = UP
                
            new_label.move_to(mid + dir_2d_name * 0.7)
            mob.become(new_label)

        def update_stack_k(mob):
            k = k_tracker.get_value()
            
            k_str = f"{k:.1f}"
            if k_str.endswith(".0"):
                k_str = k_str[:-2]
            if k_str == "-0":
                k_str = "0"
                
            new_stack = MathTex(
                r"\begin{bmatrix} " + k_str + r" \cdot -1.4 \\ " + k_str + r" \cdot 1.0 \\ " + k_str + r" \cdot -2.3 \end{bmatrix}"
            ).set_color(SUM_COLOR).scale(0.8)
            vec_val = k * vec_a_val
            
            k_sign = 1 if k >= 0 else -1
            target_pos = vec_val + k_sign * np.array([-1.5, 0.8, 0])
            
            new_stack.move_to(target_pos)
            mob.become(new_stack)

        sum_vec_origin.add_updater(update_vector_k)
        sum_label.add_updater(update_label_k)
        stack_sum_dup.add_updater(update_stack_k)

        self.play(
            k_tracker.animate.set_value(4.0),
            run_time=1.5,
            rate_func=smooth
        )

        self.play(
            k_tracker.animate.set_value(-2.0),
            run_time=3.0,
            rate_func=smooth
        )

        sum_vec_origin.remove_updater(update_vector_k)
        sum_label.remove_updater(update_label_k)
        stack_sum_dup.remove_updater(update_stack_k)
        
        # ----------------------------------------------------
        # Event 4: 01:06:08 -> t = 66.08s
        # ----------------------------------------------------
        wait_4 = max(0, 66.08 - (61.17 + 4.5))
        if wait_4 > 0:
            self.wait(wait_4)
            
        target_vec_val_neg1 = -1 * vec_a_val
        
        target_stack_neg1 = MathTex(
            r"\begin{bmatrix} 1.4 \\ -1.0 \\ 2.3 \end{bmatrix}"
        ).set_color(SUM_COLOR).scale(0.8)
        
        target_stack_pos_neg1 = target_vec_val_neg1 - np.array([-1.5, 0.8, 0])
        target_stack_neg1.move_to(target_stack_pos_neg1)
        
        anim_duration_neg1 = 2.0
        
        sum_vec_origin.add_updater(update_vector_k)
        sum_label.add_updater(update_label_k)
        
        self.play(
            k_tracker.animate.set_value(-1.0),
            Transform(stack_sum_dup, target_stack_neg1),
            run_time=anim_duration_neg1
        )
        
        sum_vec_origin.remove_updater(update_vector_k)
        sum_label.remove_updater(update_label_k)

        # ----------------------------------------------------
        # Event 5: 01:10:07 -> t = 70.12s
        # ----------------------------------------------------
        wait_5 = max(0, 70.12 - (66.08 + anim_duration_neg1))
        if wait_5 > 0:
            self.wait(wait_5)
            
        center_pos = DOWN * 2.5
        
        pink_shift = center_pos + LEFT * 1.5 - (vec_a_val / 2)
        yellow_shift = center_pos + RIGHT * 1.5 + (vec_a_val / 2)
        
        # Prepare the newly relabeled vectors
        new_pink_name = MathTex(r"\vec{v}").set_color(PINK_COLOR).scale(0.9)
        new_pink_name.move_to(vec_a_name_mob.get_center() + pink_shift)
        
        new_yellow_name = MathTex(r"-\vec{v}").set_color(SUM_COLOR).scale(0.9)
        new_yellow_name.move_to(sum_label.get_center() + yellow_shift)
        
        anim_duration_5 = 2.0
        
        # Transform handles both shifting to the new location and morphing the text simultaneously
        self.play(
            vec_a_arrow_mob.animate.shift(pink_shift),
            vec_a_label_mob.animate.shift(pink_shift),
            Transform(vec_a_name_mob, new_pink_name),
            sum_vec_origin.animate.shift(yellow_shift),
            stack_sum_dup.animate.shift(yellow_shift),
            Transform(sum_label, new_yellow_name),
            run_time=anim_duration_5
        )

        # ----------------------------------------------------
        # Event 6: 01:17:05 -> t = 77.08s
        # ----------------------------------------------------
        wait_6 = max(0, 77.08 - (70.12 + anim_duration_5))
        if wait_6 > 0:
            self.wait(wait_6)
            
        n_dir = np.array([vec_a_val[1], -vec_a_val[0], 0])
        if np.linalg.norm(n_dir) > 1e-4:
            n_dir = n_dir / np.linalg.norm(n_dir)
        else:
            n_dir = UP
            
        target_pink_start = center_pos + n_dir * 0.15 - (vec_a_val / 2)
        target_yellow_start = center_pos - n_dir * 0.15 + (vec_a_val / 2)
        
        pink_slide_offset = target_pink_start - pink_shift
        yellow_slide_offset = target_yellow_start - yellow_shift
        
        combined_stack = MathTex(
            r"\begin{bmatrix}",
            r"-1.4", r"+ 1.4", r"\\",
            r"1.0", r"- 1.0", r"\\",
            r"-2.3", r"+ 2.3",
            r"\end{bmatrix}"
        ).scale(0.8)
        
        combined_stack[1].set_color(PINK_COLOR)
        combined_stack[2].set_color(SUM_COLOR)
        combined_stack[4].set_color(PINK_COLOR)
        combined_stack[5].set_color(SUM_COLOR)
        combined_stack[7].set_color(PINK_COLOR)
        combined_stack[8].set_color(SUM_COLOR)
        
        combined_stack.move_to(center_pos + RIGHT * 3.0)
        
        def get_vis(mob):
            return VGroup(*[m.copy() for m in mob.family_members_with_points()])

        clean_vec_a_label = get_vis(vec_a_label_mob)
        clean_stack_sum = get_vis(stack_sum_dup)
        clean_combined = get_vis(combined_stack)
        clean_combined_copy = clean_combined.copy()

        self.add(clean_vec_a_label, clean_stack_sum)
        self.remove(vec_a_label_mob, stack_sum_dup)
        
        # Phase 1: Slide side-by-side & gracefully merge matrices
        self.play(
            vec_a_arrow_mob.animate.shift(pink_slide_offset),
            sum_vec_origin.animate.shift(yellow_slide_offset),
            vec_a_name_mob.animate.shift(pink_slide_offset),
            sum_label.animate.shift(yellow_slide_offset),
            ReplacementTransform(clean_vec_a_label, clean_combined),
            ReplacementTransform(clean_stack_sum, clean_combined_copy),
            run_time=2.0
        )
        self.remove(clean_combined_copy)
        
        def shrink_pink(mob, alpha):
            length_factor = 1.0 - alpha * 0.9999
            mob.set_start_and_end(target_pink_start, target_pink_start + vec_a_val * length_factor)
            
        def shrink_yellow(mob, alpha):
            length_factor = 1.0 - alpha * 0.9999
            mob.set_start_and_end(target_yellow_start, target_yellow_start - vec_a_val * length_factor)
            
        # Phase 2: Shrink the vectors down to near-zero while pulling the labels in tight
        self.play(
            UpdateFromAlphaFunc(vec_a_arrow_mob, shrink_pink),
            UpdateFromAlphaFunc(sum_vec_origin, shrink_yellow),
            vec_a_name_mob.animate.move_to(center_pos + LEFT * 0.4),
            sum_label.animate.move_to(center_pos + RIGHT * 0.4),
            run_time=1.5
        )
        
        zero_stack = MathTex(
            r"\begin{bmatrix} 0 \\ 0 \\ 0 \end{bmatrix}"
        ).scale(0.8).set_color(WHITE).move_to(clean_combined)
        
        zero_label = MathTex(r"\vec{0}").scale(0.9).set_color(WHITE).move_to(center_pos)
        
        clean_zero_stack = get_vis(zero_stack)
        clean_zero_label = get_vis(zero_label)
        clean_zero_label_copy = clean_zero_label.copy()
        
        clean_vec_a_name = get_vis(vec_a_name_mob)
        clean_sum_label = get_vis(sum_label)
        
        self.add(clean_vec_a_name, clean_sum_label)
        self.remove(vec_a_name_mob, sum_label)
        
        flash_pink = vec_a_arrow_mob.copy().set_color(WHITE)
        flash_yellow = sum_vec_origin.copy().set_color(WHITE)
        
        self.add(flash_pink, flash_yellow)
        self.remove(vec_a_arrow_mob, sum_vec_origin)
        
        # Phase 3: Flash, fade out, and safely merge the zero results 
        self.play(
            FadeOut(flash_pink, scale=2.0),
            FadeOut(flash_yellow, scale=2.0),
            ReplacementTransform(clean_combined, clean_zero_stack),
            ReplacementTransform(clean_vec_a_name, clean_zero_label),
            ReplacementTransform(clean_sum_label, clean_zero_label_copy),
            run_time=1.0
        )
        self.remove(clean_zero_label_copy)

        # ----------------------------------------------------
        # Event 7: 01:22:11 -> t = 82.18s
        # ----------------------------------------------------
        wait_7 = max(0, 82.18 - (77.08 + 4.5))
        if wait_7 > 0:
            self.wait(wait_7)

        self.play(
            FadeOut(clean_zero_stack),
            FadeOut(clean_zero_label),
            run_time=1.0
        )

        # ----------------------------------------------------
        # Video-Editing Tail
        # ----------------------------------------------------
        self.wait(10.0)



class Scene21(ThreeDScene):
    def construct(self):
        # ----------------------------------------------------
        # Static Recreation of Scene 20 Final Frame
        # ----------------------------------------------------
        self.set_camera_orientation(phi=0, theta=-PI/2, zoom=0.66, focal_distance=100.0)
        
        # Axes
        axis_opacity = 0.3
        axis_y = Line(DOWN * 20, UP * 20, color=WHITE, stroke_opacity=axis_opacity)
        axis_1 = Line(LEFT * 20 + DOWN * 6, RIGHT * 20 + UP * 6, color=WHITE, stroke_opacity=axis_opacity)
        axis_2 = Line(LEFT * 20 + UP * 6, RIGHT * 20 + DOWN * 6, color=WHITE, stroke_opacity=axis_opacity)
        axes = VGroup(axis_y, axis_1, axis_2)
        self.add(axes)
        
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"
        
        vec_b_val = np.array([-2.1, -1.5, -1.5])
        vec_c_val = np.array([3.2, -0.2, -0.5])
        
        vectors = [
            (vec_b_val, PURPLE_COLOR, r"\vec{b}"),
            (vec_c_val, BLUE_COLOR, r"\vec{c}")
        ]
        
        b_items = {}
        c_items = {}
        
        for pos, color, name in vectors:
            arrow = CameraFacingArrow(
                start=ORIGIN, 
                end=pos, 
                color=color, 
                tip_length=0.35, 
                camera_dir=OUT
            )
            self.add(arrow)
            
            x, y, z = pos
            vec_label = MathTex(
                r"\begin{bmatrix} %.1f \\ %.1f \\ %.1f \end{bmatrix}" % (x, y, z)
            ).scale(0.6).set_color(color)
            
            dir_2d = np.array([x, y, 0])
            if np.linalg.norm(dir_2d) > 0:
                dir_2d = dir_2d / np.linalg.norm(dir_2d)
            else:
                dir_2d = RIGHT
                
            vec_label.next_to(pos, dir_2d, buff=0.2)
            self.add(vec_label)
            
            mid = pos / 2
            dir_2d_name = np.array([-pos[1], pos[0], 0])
            if np.linalg.norm(dir_2d_name) > 1e-4:
                dir_2d_name = dir_2d_name / np.linalg.norm(dir_2d_name)
            else:
                dir_2d_name = UP
                
            name_label = MathTex(name).set_color(color).scale(0.9)
            name_label.move_to(mid + dir_2d_name * 0.35)
            self.add(name_label)
            
            if name == r"\vec{b}":
                b_items['arrow'] = arrow
                b_items['stack'] = vec_label
                b_items['name'] = name_label
            else:
                c_items['arrow'] = arrow
                c_items['stack'] = vec_label
                c_items['name'] = name_label

        # ----------------------------------------------------
        # Scene 21 Start (01:23:20 -> t = 83.333s)
        # ----------------------------------------------------
        
        # Event 1: 01:37:17 -> t = 97.283s
        wait_1 = max(0, 97.283 - 83.333)
        self.wait(wait_1)
        
        target_b_val = np.array([3.5, 0.0, 0.0])
        target_c_val = np.array([2.2, 0.0, 1.3])
        
        target_label_b = MathTex(r"\vec{b}").set_color(PURPLE_COLOR).scale(0.9)
        target_label_b.rotate(PI/2, RIGHT)
        target_label_b.move_to(target_b_val / 2 + np.array([0.0, 0.0, -0.4]))
        
        target_label_a = MathTex(r"\vec{a}").set_color(PINK_COLOR).scale(0.9)
        target_label_a.rotate(PI/2, RIGHT)
        target_label_a.move_to(target_c_val / 2 + np.array([-0.2, 0.0, 0.4]))
        
        def update_arrow_b(mob, alpha):
            current = vec_b_val + alpha * (target_b_val - vec_b_val)
            
            phi_current = 0 + alpha * (PI / 2)
            mob.camera_dir = np.array([0, -np.sin(phi_current), np.cos(phi_current)])
            
            mob.set_start_and_end(ORIGIN, current)
            
        def update_arrow_c(mob, alpha):
            current = vec_c_val + alpha * (target_c_val - vec_c_val)
            
            phi_current = 0 + alpha * (PI / 2)
            mob.camera_dir = np.array([0, -np.sin(phi_current), np.cos(phi_current)])
            
            new_color = interpolate_color(ManimColor(BLUE_COLOR), ManimColor(PINK_COLOR), alpha)
            mob.color = new_color
            mob.set_color(new_color)
            
            mob.set_start_and_end(ORIGIN, current)
            
        self.move_camera(
            phi=PI/2,
            theta=-PI/2,
            zoom=1.0,  # This aligns the 3D camera scale with a standard 2D Scene
            run_time=3.0,
            added_anims=[
                UpdateFromAlphaFunc(b_items['arrow'], update_arrow_b),
                UpdateFromAlphaFunc(c_items['arrow'], update_arrow_c),
                Transform(b_items['name'], target_label_b),
                Transform(c_items['name'], target_label_a),
                FadeOut(axes),
                FadeOut(b_items['stack']),
                FadeOut(c_items['stack'])
            ]
        )
        
        # ----------------------------------------------------
        # Video-Editing Tail
        # ----------------------------------------------------
        self.wait(10.0)



class CustomArrow2D(VGroup):
    def __init__(self, start, end, color, tip_length=0.35, stroke_width=6, **kwargs):
        super().__init__(**kwargs)
        self.start_pt = np.array(start, dtype=float)
        self.end_pt = np.array(end, dtype=float)
        self.color = color
        self.tip_length = tip_length
        self.stroke_width = stroke_width
        
        self.line = Line(LEFT, RIGHT, color=self.color, stroke_width=self.stroke_width, buff=0)
        self.tip = Polygon(ORIGIN, RIGHT, UP, fill_color=self.color, fill_opacity=1, stroke_width=0)
        
        self.add(self.line, self.tip)
        self.update_geometry()
        
    def set_start_and_end(self, start, end):
        self.start_pt = np.array(start, dtype=float)
        self.end_pt = np.array(end, dtype=float)
        self.update_geometry()
        
    def update_geometry(self):
        d = self.end_pt - self.start_pt
        length = np.linalg.norm(d)
        
        if length < 1e-4:
            d = np.array([1e-4, 0, 0])
            length = 1e-4
            self.tip.set_opacity(0)
            self.line.set_opacity(0)
        else:
            self.tip.set_opacity(1)
            self.line.set_opacity(1)
            
        d = d / length
        
        actual_tip_length = min(self.tip_length, length)
        actual_tip_width = actual_tip_length * 0.8
        
        r = np.array([-d[1], d[0], 0])
        
        safe_end_pt = self.start_pt + d * length
        line_end = safe_end_pt - actual_tip_length * d
        
        if np.linalg.norm(line_end - self.start_pt) < 1e-4:
            line_end = self.start_pt + d * 1e-4
            
        self.line.put_start_and_end_on(self.start_pt, line_end)
        
        p0 = safe_end_pt
        p1 = safe_end_pt - actual_tip_length * d + (actual_tip_width / 2) * r
        p2 = safe_end_pt - actual_tip_length * d - (actual_tip_width / 2) * r
        
        current_opacity = self.tip.get_fill_opacity()
        self.tip.become(Polygon(p0, p1, p2, fill_color=self.color, fill_opacity=current_opacity, stroke_width=0))



class Scene22(Scene):
    def construct(self):
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"

        # ----------------------------------------------------
        # Static Recreation of Scene 21 Final Frame (in 2D)
        # ----------------------------------------------------
        
        vec_b_val = np.array([3.5, 0.0, 0.0])
        vec_a_val = np.array([2.2, 1.3, 0.0])

        # Initialized with CustomArrow2D to maintain identical geometry to Scene 21
        vec_b = CustomArrow2D(start=ORIGIN, end=vec_b_val, color=PURPLE_COLOR, tip_length=0.35, stroke_width=6)
        vec_a = CustomArrow2D(start=ORIGIN, end=vec_a_val, color=PINK_COLOR, tip_length=0.35, stroke_width=6)

        label_b = MathTex(r"\vec{b}").set_color(PURPLE_COLOR).scale(0.9)
        label_b.move_to(vec_b_val / 2 + DOWN * 0.4)

        label_a = MathTex(r"\vec{a}").set_color(PINK_COLOR).scale(0.9)
        label_a_offset = np.array([-0.2, 0.4, 0.0])
        label_a.move_to(vec_a_val / 2 + label_a_offset)

        self.add(vec_b, vec_a, label_b, label_a)

        # ----------------------------------------------------
        # Scene 22 Start (01:41:05 -> t = 101.083s)
        # ----------------------------------------------------
        
        # Event 1: 01:43:16 -> t = 103.267s
        wait_1 = max(0, 103.267 - 101.083)
        if wait_1 > 0:
            self.wait(wait_1)

        base_angle = np.arctan2(vec_a_val[1], vec_a_val[0])
        len_a = np.linalg.norm(vec_a_val)
        
        angle_tracker = ValueTracker(base_angle)

        def update_arrow_a(mob):
            theta = angle_tracker.get_value()
            new_end = np.array([np.cos(theta), np.sin(theta), 0.0]) * len_a
            mob.set_start_and_end(ORIGIN, new_end)

        def update_label_a(mob):
            theta = angle_tracker.get_value()
            new_end = np.array([np.cos(theta), np.sin(theta), 0.0]) * len_a
            mid = new_end / 2
            
            delta = theta - base_angle
            rot = np.array([
                [np.cos(delta), -np.sin(delta), 0],
                [np.sin(delta),  np.cos(delta), 0],
                [0,              0,             1]
            ])
            current_offset = np.dot(rot, label_a_offset)
            mob.move_to(mid + current_offset)

        vec_a.add_updater(update_arrow_a)
        label_a.add_updater(update_label_a)

        # Snap 1: Close
        self.play(angle_tracker.animate.set_value(0.0), run_time=0.15, rate_func=rush_into)
        # Snap 1: Open partially 
        self.play(angle_tracker.animate.set_value(base_angle * 0.5), run_time=0.15, rate_func=rush_from)
        # Snap 2: Close again
        self.play(angle_tracker.animate.set_value(0.0), run_time=0.15, rate_func=rush_into)
        # Snap 2: Open fully 
        self.play(angle_tracker.animate.set_value(base_angle), run_time=0.25, rate_func=rush_from)

        vec_a.remove_updater(update_arrow_a)
        label_a.remove_updater(update_label_a)

        # ----------------------------------------------------
        # Event 2: 01:49:22 -> t = 109.367s
        # ----------------------------------------------------
        time_after_snap = 103.267 + 0.15 + 0.15 + 0.15 + 0.25
        wait_2 = max(0, 109.367 - time_after_snap)
        if wait_2 > 0:
            self.wait(wait_2)
            
        vec_a.add_updater(update_arrow_a)
        label_a.add_updater(update_label_a)
        
        # Slower, calmer close
        self.play(angle_tracker.animate.set_value(0.0), run_time=1.5, rate_func=smooth)
        
        vec_a.remove_updater(update_arrow_a)
        label_a.remove_updater(update_label_a)

        # ----------------------------------------------------
        # Event 3: 01:55:01 -> t = 115.017s
        # ----------------------------------------------------
        time_after_close = 109.367 + 1.5
        wait_3 = max(0, 115.017 - time_after_close)
        if wait_3 > 0:
            self.wait(wait_3)
            
        eq_line = MathTex(r"\vec{a} \triangleq a \hat{a}", r"\quad", r"\vec{b} \triangleq b \hat{b}")
        eq_line[0].set_color(PINK_COLOR)
        eq_line[2].set_color(PURPLE_COLOR)
        
        diagram_center = VGroup(vec_a, vec_b).get_center()
        eq_line.next_to(diagram_center, DOWN, buff=1.5)
        
        footnote = Tex(
            r"*\textit{$\triangleq$ is used to mean ``this new notation is such that both expressions are equal''}",
            color=LIGHT_GREY
        ).scale(0.65).to_edge(DOWN, buff=0.5)
        
        label_a_hat = MathTex(r"a \hat{a}").set_color(PINK_COLOR).scale(0.9).move_to(label_a.get_center())
        label_b_hat = MathTex(r"b \hat{b}").set_color(PURPLE_COLOR).scale(0.9).move_to(label_b.get_center())
        
        anim_dur_3 = 3.0
        self.play(
            Write(eq_line),
            FadeIn(footnote),
            Transform(label_a, label_a_hat),
            Transform(label_b, label_b_hat),
            run_time=anim_dur_3
        )

        # ----------------------------------------------------
        # Event 4: 02:01:06 -> t = 121.100s
        # ----------------------------------------------------
        time_after_eq = 115.017 + anim_dur_3
        wait_4 = max(0, 121.100 - time_after_eq)
        if wait_4 > 0:
            self.wait(wait_4)
            
        label_a_bhat = MathTex(r"a", r"\hat{b}").scale(0.9)
        label_a_bhat[0].set_color(PINK_COLOR)
        label_a_bhat[1].set_color(PURPLE_COLOR)
        
        label_a_bhat.move_to(label_a.get_center())
        target_x = len_a + 0.2 + label_a_bhat.width / 2
        label_a_bhat.set_x(target_x)
        
        anim_dur_4 = 1.0
        self.play(
            Transform(label_a, label_a_bhat),
            run_time=anim_dur_4
        )

        # ----------------------------------------------------
        # Event 5: 02:06:09 -> t = 126.150s
        # ----------------------------------------------------
        time_after_bhat = 121.100 + anim_dur_4
        wait_5 = max(0, 126.150 - time_after_bhat)
        if wait_5 > 0:
            self.wait(wait_5)
            
        # Target native arrows for calculating final label positions exactly as they will be in Scene 23
        target_vec_a = Arrow(ORIGIN, vec_a_val, color=PINK_COLOR, buff=0, stroke_width=6, tip_length=0.35)
        target_vec_b = Arrow(ORIGIN, vec_b_val, color=PURPLE_COLOR, buff=0, stroke_width=6, tip_length=0.35)
        
        orig_label_a = MathTex(r"\vec{a}").set_color(PINK_COLOR).scale(0.9)
        orig_label_a.next_to(target_vec_a.get_end(), UP * 0.2)
        
        orig_label_b = MathTex(r"\vec{b}").set_color(PURPLE_COLOR).scale(0.9)
        orig_label_b.next_to(target_vec_b.get_end(), DOWN * 0.4 + RIGHT * 0.1)
        
        # Invisibly swap custom arrows for Manim native arrows while they are overlapping closed
        # This completely circumvents morphing algorithms, allowing rigid rotation using standard updaters
        closed_end_a = np.array([len_a, 0.0, 0.0])
        native_vec_a = Arrow(ORIGIN, closed_end_a, color=PINK_COLOR, buff=0, stroke_width=6, tip_length=0.35)
        native_vec_b = Arrow(ORIGIN, vec_b_val, color=PURPLE_COLOR, buff=0, stroke_width=6, tip_length=0.35)
        
        self.remove(vec_a, vec_b)
        self.add(native_vec_b, native_vec_a)
        
        def update_native_a(mob):
            theta = angle_tracker.get_value()
            new_end = np.array([np.cos(theta), np.sin(theta), 0.0]) * len_a
            mob.put_start_and_end_on(ORIGIN, new_end)
            
        native_vec_a.add_updater(update_native_a)
        
        # path_arc forces label_a to elegantly orbit along with the newly rigid vector
        self.play(
            FadeOut(eq_line),
            FadeOut(footnote),
            Transform(label_a, orig_label_a, path_arc=base_angle),
            Transform(label_b, orig_label_b),
            angle_tracker.animate.set_value(base_angle),
            run_time=2.0, 
            rate_func=smooth
        )
        
        native_vec_a.remove_updater(update_native_a)

        # ----------------------------------------------------
        # Video-Editing Tail
        # ----------------------------------------------------
        self.wait(10.0)
        # ----------------------------------------------------
        self.wait(10.0)



class Scene23(Scene):
    def construct(self):
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"

        # ----------------------------------------------------
        # Static Recreation of Scene 22 Final Frame
        # ----------------------------------------------------
        
        vec_b_val = np.array([3.5, 0.0, 0.0])
        vec_a_val = np.array([2.2, 1.3, 0.0])

        vec_b = Arrow(ORIGIN, vec_b_val, color=PURPLE_COLOR, buff=0, stroke_width=6, tip_length=0.35)
        vec_a = Arrow(ORIGIN, vec_a_val, color=PINK_COLOR, buff=0, stroke_width=6, tip_length=0.35)

        label_b = MathTex(r"\vec{b}").set_color(PURPLE_COLOR).scale(0.9)
        label_b.next_to(vec_b.get_end(), DOWN * 0.4 + RIGHT * 0.1)

        label_a = MathTex(r"\vec{a}").set_color(PINK_COLOR).scale(0.9)
        label_a.next_to(vec_a.get_end(), UP * 0.2)

        self.add(vec_b, vec_a, label_b, label_a)

        # ----------------------------------------------------
        # Scene 23 Start (02:08:15 -> t = 128.250s)
        # ----------------------------------------------------
        
        # Event 1: 02:11:02 -> t = 131.033s
        wait_1 = max(0, 131.033 - 128.250)
        if wait_1 > 0:
            self.wait(wait_1)

        proj_point = np.array([vec_a_val[0], 0.0, 0.0])
        
        proj_line = DashedLine(vec_a_val, proj_point, color=WHITE)
        
        shadow_glow = create_hazy_line(
            start_pt=ORIGIN,
            end_pt=proj_point,
            color=PINK_COLOR,
            core_width=0.05,
            glow_radius=0.40,
            num_layers=30,
            opacity=1.0
        )

        anim_1_dur = 0.5
        self.play(
            Create(proj_line),
            FadeIn(shadow_glow),
            run_time=anim_1_dur
        )

        # ----------------------------------------------------
        # Event 2: 02:14:02 -> t = 134.033s
        # ----------------------------------------------------
        wait_2 = max(0, 134.033 - (131.033 + anim_1_dur))
        if wait_2 > 0:
            self.wait(wait_2)
            
        proxy_line_b = Line(ORIGIN, vec_b_val)
        proxy_line_a = Line(ORIGIN, vec_a_val)
        
        angle = Angle(proxy_line_b, proxy_line_a, radius=0.7, color=BLUE_COLOR)
        angle_label = MathTex(r"\theta", color=BLUE_COLOR).scale(0.8)
        angle_label.next_to(angle, RIGHT, buff=0.1).shift(UP * 0.1)

        anim_2_dur = 1.0
        self.play(
            Create(angle),
            Write(angle_label),
            run_time=anim_2_dur
        )

        # ----------------------------------------------------
        # Event 3: 02:16:13 -> t = 136.217s
        # ----------------------------------------------------
        wait_3 = max(0, 136.217 - (134.033 + anim_2_dur))
        if wait_3 > 0:
            self.wait(wait_3)
            
        comp_label = MathTex(r"a", r"\cos \theta", r"\hat{b}").scale(0.9)
        comp_label[0].set_color(PINK_COLOR)
        comp_label[1].set_color(BLUE_COLOR)
        comp_label[2].set_color(PURPLE_COLOR)
        
        comp_label.next_to(shadow_glow, DOWN, buff=0.2)

        anim_3_dur = 1.0
        self.play(
            Write(comp_label),
            run_time=anim_3_dur
        )

        # ----------------------------------------------------
        # Event 4: 02:23:01 -> t = 143.017s
        # ----------------------------------------------------
        time_after_event_3 = 136.217 + anim_3_dur
        wait_4 = max(0, 143.017 - time_after_event_3)
        if wait_4 > 0:
            self.wait(wait_4)
            
        a_dot_b = np.dot(vec_a_val, vec_b_val)
        a_mag_sq = np.dot(vec_a_val, vec_a_val)
        proj_b_val = (a_dot_b / a_mag_sq) * vec_a_val
        
        proj_line_2 = DashedLine(vec_b_val, proj_b_val, color=WHITE)
        
        shadow_glow_2 = create_hazy_line(
            start_pt=vec_a_val,
            end_pt=proj_b_val,
            color=PURPLE_COLOR,
            core_width=0.05,
            glow_radius=0.40,
            num_layers=30,
            opacity=1.0
        )
        
        anim_4_dur = 1.0
        self.play(
            Create(proj_line_2),
            FadeIn(shadow_glow_2),
            run_time=anim_4_dur
        )

        # ----------------------------------------------------
        # Event 5: 02:25:02 -> t = 145.033s
        # ----------------------------------------------------
        time_after_event_4 = 143.017 + anim_4_dur
        wait_5 = max(0, 145.033 - time_after_event_4)
        if wait_5 > 0:
            self.wait(wait_5)
            
        comp_label_2 = MathTex(r"b", r"\cos \theta", r"\hat{a}").scale(0.9)
        comp_label_2[0].set_color(PURPLE_COLOR)
        comp_label_2[1].set_color(BLUE_COLOR)
        comp_label_2[2].set_color(PINK_COLOR)
        
        comp_label_2.next_to(proj_b_val, RIGHT, buff=0.15).shift(UP * 0.15)

        anim_5_dur = 1.0
        self.play(
            Write(comp_label_2),
            run_time=anim_5_dur
        )

        # ----------------------------------------------------
        # Event 6: 02:50:13 -> t = 170.217s
        # ----------------------------------------------------
        time_after_event_5 = 145.033 + anim_5_dur
        wait_6 = max(0, 170.217 - time_after_event_5)
        if wait_6 > 0:
            self.wait(wait_6)
            
        comp_label_ab = MathTex(r"a", r"b", r"\cos \theta", r"\hat{b}").scale(0.9)
        comp_label_ab[0].set_color(PINK_COLOR)
        comp_label_ab[1].set_color(PURPLE_COLOR)
        comp_label_ab[2].set_color(BLUE_COLOR)
        comp_label_ab[3].set_color(PURPLE_COLOR)
        
        comp_label_ab.next_to(shadow_glow, DOWN, buff=0.2)

        anim_6_dur = 1.0
        self.play(
            ReplacementTransform(comp_label, comp_label_ab),
            run_time=anim_6_dur
        )

        # ----------------------------------------------------
        # Event 7: 02:56:04 -> t = 176.067s
        # ----------------------------------------------------
        time_after_event_6 = 170.217 + anim_6_dur
        wait_7 = max(0, 176.067 - time_after_event_6)
        if wait_7 > 0:
            self.wait(wait_7)
            
        comp_label_ba = MathTex(r"b", r"a", r"\cos \theta", r"\hat{a}").scale(0.9)
        comp_label_ba[0].set_color(PURPLE_COLOR)
        comp_label_ba[1].set_color(PINK_COLOR)
        comp_label_ba[2].set_color(BLUE_COLOR)
        comp_label_ba[3].set_color(PINK_COLOR)
        
        comp_label_ba.next_to(proj_b_val, RIGHT, buff=0.15).shift(UP * 0.15)

        anim_7_dur = 1.0
        self.play(
            ReplacementTransform(comp_label_2, comp_label_ba),
            run_time=anim_7_dur
        )

        # ----------------------------------------------------
        # Event 8: 03:03:14 -> t = 183.233s
        # ----------------------------------------------------
        time_after_event_7 = 176.067 + anim_7_dur
        wait_8 = max(0, 183.233 - time_after_event_7)
        if wait_8 > 0:
            self.wait(wait_8)
            
        eq_final = MathTex(r"a", r"b", r"\cos \theta", r"=", r"b", r"a", r"\cos \theta").scale(1.0)
        eq_final[0].set_color(PINK_COLOR)
        eq_final[1].set_color(PURPLE_COLOR)
        eq_final[2].set_color(BLUE_COLOR)
        eq_final[4].set_color(PURPLE_COLOR)
        eq_final[5].set_color(PINK_COLOR)
        eq_final[6].set_color(BLUE_COLOR)
        
        # Position equation well below the vectors and shadows
        eq_final.move_to(DOWN * 2.5)

        anim_8_dur = 2.0
        self.play(
            ReplacementTransform(comp_label_ab[0:3].copy(), eq_final[0:3]),
            ReplacementTransform(comp_label_ba[0:3].copy(), eq_final[4:7]),
            Write(eq_final[3]),
            run_time=anim_8_dur
        )

        # ----------------------------------------------------
        # Video-Editing Tail
        # ----------------------------------------------------
        self.wait(10.0)
        
        
        
        
class Scene24(Scene):
    def construct(self):
        PURPLE_COLOR = "#9B51E0"
        PINK_COLOR = "#FF6B9B"
        BLUE_COLOR = "#56CCF2"

        # ----------------------------------------------------
        # Static Recreation of Scene 23 Final Frame
        # ----------------------------------------------------
        
        vec_b_val = np.array([3.5, 0.0, 0.0])
        vec_a_val = np.array([2.2, 1.3, 0.0])

        vec_b = Arrow(ORIGIN, vec_b_val, color=PURPLE_COLOR, buff=0, stroke_width=6, tip_length=0.35)
        vec_a = Arrow(ORIGIN, vec_a_val, color=PINK_COLOR, buff=0, stroke_width=6, tip_length=0.35)

        label_b = MathTex(r"\vec{b}").set_color(PURPLE_COLOR).scale(0.9)
        label_b.next_to(vec_b.get_end(), DOWN * 0.4 + RIGHT * 0.1)

        label_a = MathTex(r"\vec{a}").set_color(PINK_COLOR).scale(0.9)
        label_a.next_to(vec_a.get_end(), UP * 0.2)

        proj_point = np.array([vec_a_val[0], 0.0, 0.0])
        proj_line = DashedLine(vec_a_val, proj_point, color=WHITE)
        shadow_glow = create_hazy_line(
            start_pt=ORIGIN,
            end_pt=proj_point,
            color=PINK_COLOR,
            core_width=0.05,
            glow_radius=0.40,
            num_layers=30,
            opacity=1.0
        )

        proxy_line_b = Line(ORIGIN, vec_b_val)
        proxy_line_a = Line(ORIGIN, vec_a_val)
        angle = Angle(proxy_line_b, proxy_line_a, radius=0.7, color=BLUE_COLOR)
        angle_label = MathTex(r"\theta", color=BLUE_COLOR).scale(0.8)
        angle_label.next_to(angle, RIGHT, buff=0.1).shift(UP * 0.1)

        a_dot_b = np.dot(vec_a_val, vec_b_val)
        a_mag_sq = np.dot(vec_a_val, vec_a_val)
        proj_b_val = (a_dot_b / a_mag_sq) * vec_a_val
        
        proj_line_2 = DashedLine(vec_b_val, proj_b_val, color=WHITE)
        shadow_glow_2 = create_hazy_line(
            start_pt=vec_a_val,
            end_pt=proj_b_val,
            color=PURPLE_COLOR,
            core_width=0.05,
            glow_radius=0.40,
            num_layers=30,
            opacity=1.0
        )

        comp_label_ab = MathTex(r"a", r"b", r"\cos \theta", r"\hat{b}").scale(0.9)
        comp_label_ab[0].set_color(PINK_COLOR)
        comp_label_ab[1].set_color(PURPLE_COLOR)
        comp_label_ab[2].set_color(BLUE_COLOR)
        comp_label_ab[3].set_color(PURPLE_COLOR)
        comp_label_ab.next_to(shadow_glow, DOWN, buff=0.2)

        comp_label_ba = MathTex(r"b", r"a", r"\cos \theta", r"\hat{a}").scale(0.9)
        comp_label_ba[0].set_color(PURPLE_COLOR)
        comp_label_ba[1].set_color(PINK_COLOR)
        comp_label_ba[2].set_color(BLUE_COLOR)
        comp_label_ba[3].set_color(PINK_COLOR)
        comp_label_ba.next_to(proj_b_val, RIGHT, buff=0.15).shift(UP * 0.15)

        eq_final = MathTex(r"a", r"b", r"\cos \theta", r"=", r"b", r"a", r"\cos \theta").scale(1.0)
        eq_final[0].set_color(PINK_COLOR)
        eq_final[1].set_color(PURPLE_COLOR)
        eq_final[2].set_color(BLUE_COLOR)
        eq_final[4].set_color(PURPLE_COLOR)
        eq_final[5].set_color(PINK_COLOR)
        eq_final[6].set_color(BLUE_COLOR)
        eq_final.move_to(DOWN * 2.5)

        self.add(
            vec_b, vec_a, label_b, label_a,
            proj_line, shadow_glow,
            angle, angle_label,
            proj_line_2, shadow_glow_2,
            comp_label_ab, comp_label_ba,
            eq_final
        )

        # ----------------------------------------------------
        # Scene 24 Start (03:06:13 -> t = 186.217s)
        # ----------------------------------------------------
        
        # Event 1: 03:09:16 -> t = 189.267s
        wait_1 = max(0, 189.267 - 186.217)
        if wait_1 > 0:
            self.wait(wait_1)
            
        new_eq = MathTex(r"\vec{a}", r"\cdot", r"\vec{b}", r"=", r"a", r"b", r"\cos \theta").scale(1.0)
        new_eq[0].set_color(PINK_COLOR)
        new_eq[2].set_color(PURPLE_COLOR)
        new_eq[4].set_color(PINK_COLOR)
        new_eq[5].set_color(PURPLE_COLOR)
        new_eq[6].set_color(BLUE_COLOR)
        new_eq.move_to(eq_final.get_center())

        new_comp_label_ab = MathTex(r"\vec{a}", r"\cdot", r"\vec{b}", r"\; \hat{b}").scale(0.9)
        new_comp_label_ab[0].set_color(PINK_COLOR)
        new_comp_label_ab[2].set_color(PURPLE_COLOR)
        new_comp_label_ab[3].set_color(PURPLE_COLOR)
        new_comp_label_ab.next_to(shadow_glow, DOWN, buff=0.2)

        new_comp_label_ba = MathTex(r"\vec{a}", r"\cdot", r"\vec{b}", r"\; \hat{a}").scale(0.9)
        new_comp_label_ba[0].set_color(PINK_COLOR)
        new_comp_label_ba[2].set_color(PURPLE_COLOR)
        new_comp_label_ba[3].set_color(PINK_COLOR)
        new_comp_label_ba.next_to(proj_b_val, RIGHT, buff=0.15).shift(UP * 0.15)

        anim_1_dur = 1.5
        self.play(
            ReplacementTransform(eq_final[0:3], new_eq[0:3]),
            ReplacementTransform(eq_final[3], new_eq[3]),
            ReplacementTransform(eq_final[4], new_eq[5]),
            ReplacementTransform(eq_final[5], new_eq[4]),
            ReplacementTransform(eq_final[6], new_eq[6]),
            ReplacementTransform(comp_label_ab, new_comp_label_ab),
            ReplacementTransform(comp_label_ba, new_comp_label_ba),
            run_time=anim_1_dur
        )

        # ----------------------------------------------------
        # Event 2: 03:24:08 -> t = 204.133s
        # ----------------------------------------------------
        time_after_event_1 = 189.267 + anim_1_dur
        wait_2 = max(0, 204.133 - time_after_event_1)
        if wait_2 > 0:
            self.wait(wait_2)

        full_label_a = MathTex(r"\vec{a} = \begin{pmatrix} a_x \\ a_y \\ a_z \end{pmatrix}").set_color(PINK_COLOR).scale(0.75)
        full_label_a.next_to(vec_a.get_end(), UP * 0.4 + LEFT * 1.0)

        full_label_b = MathTex(r"\vec{b} = \begin{pmatrix} b_x \\ b_y \\ b_z \end{pmatrix}").set_color(PURPLE_COLOR).scale(0.75)
        full_label_b.next_to(vec_b.get_end(), DOWN * 0.6 + RIGHT * 0.2)

        anim_2_dur = 1.5
        self.play(
            ReplacementTransform(label_a, full_label_a),
            ReplacementTransform(label_b, full_label_b),
            run_time=anim_2_dur
        )

        # ----------------------------------------------------
        # Event 3: 03:26:04 -> t = 206.067s
        # ----------------------------------------------------
        time_after_event_2 = 204.133 + anim_2_dur
        wait_3 = max(0, 206.067 - time_after_event_2)
        if wait_3 > 0:
            self.wait(wait_3)

        new_angle_label = MathTex(r"\theta = ??", color=BLUE_COLOR).scale(0.8)
        new_angle_label.next_to(angle, RIGHT, buff=0.15).shift(UP * 0.15)

        anim_3_dur = 2.5
        self.play(
            ReplacementTransform(angle_label, new_angle_label),
            run_time=anim_3_dur
        )

        # ----------------------------------------------------
        # Event 4: 03:38:19 -> t = 218.317s
        # ----------------------------------------------------
        time_after_event_3 = 206.067 + anim_3_dur
        wait_4 = max(0, 218.317 - time_after_event_3)
        if wait_4 > 0:
            self.wait(wait_4)

        unit_origin = LEFT * 5.2 + DOWN * 0.2
        unit_x = Arrow(unit_origin, unit_origin + RIGHT * 1.2, color=WHITE, buff=0, stroke_width=4, tip_length=0.25)
        unit_y = Arrow(unit_origin, unit_origin + UP * 1.2, color=WHITE, buff=0, stroke_width=4, tip_length=0.25)

        label_x = MathTex(r"\hat{x}", color=WHITE).scale(0.85).next_to(unit_x.get_end(), RIGHT * 0.2)
        label_y = MathTex(r"\hat{y}", color=WHITE).scale(0.85).next_to(unit_y.get_end(), UP * 0.2)

        anim_4_dur = 1.5
        self.play(
            Create(unit_x),
            Create(unit_y),
            Write(label_x),
            Write(label_y),
            run_time=anim_4_dur
        )

        # ----------------------------------------------------
        # Event 5: 03:42:18 -> t = 222.300s
        # ----------------------------------------------------
        time_after_event_4 = 218.317 + anim_4_dur
        wait_5 = max(0, 222.300 - time_after_event_4)
        if wait_5 > 0:
            self.wait(wait_5)

        xy_dot_eq = MathTex(r"\hat{x} \cdot \hat{y} = 0", color=WHITE).scale(0.85)
        xy_dot_eq.next_to(VGroup(unit_x, unit_y), DOWN, buff=0.5).set_x(unit_origin[0] + 0.6)

        anim_5_dur = 1.0
        self.play(
            Write(xy_dot_eq),
            run_time=anim_5_dur
        )

        # ----------------------------------------------------
        # Event 6: 03:48:19 -> t = 228.317s
        # ----------------------------------------------------
        time_after_event_5 = 222.300 + anim_5_dur
        wait_6 = max(0, 228.317 - time_after_event_5)
        if wait_6 > 0:
            self.wait(wait_6)

        xx_dot_eq = MathTex(r"\hat{x} \cdot \hat{x} = |\hat{x}| |\hat{x}|", color=WHITE).scale(0.85)
        xx_dot_eq.next_to(xy_dot_eq, DOWN, buff=0.25).align_to(xy_dot_eq, LEFT)

        anim_6_dur = 1.0
        self.play(
            Write(xx_dot_eq),
            run_time=anim_6_dur
        )

        # ----------------------------------------------------
        # Event 7: 03:51:18 -> t = 231.300s
        # ----------------------------------------------------
        time_after_event_6 = 228.317 + anim_6_dur
        wait_7 = max(0, 231.300 - time_after_event_6)
        if wait_7 > 0:
            self.wait(wait_7)

        one_eq = MathTex(r"= 1", color=WHITE).scale(0.85)
        one_eq.next_to(xx_dot_eq, RIGHT, buff=0.15)

        anim_7_dur = 1.0
        self.play(
            Write(one_eq),
            run_time=anim_7_dur
        )

        # ----------------------------------------------------
        # Event 8: 03:55:00 -> t = 235.000s
        # ----------------------------------------------------
        time_after_event_7 = 231.300 + anim_7_dur
        wait_8 = max(0, 235.000 - time_after_event_7)
        if wait_8 > 0:
            self.wait(wait_8)

        diag_offset = RIGHT * 2.5 + UP * 1.5
        target_proj_point = diag_offset + RIGHT * 2.2

        scene1_label_a = MathTex(r"\vec{a}", color=PINK_COLOR).scale(0.9)
        scene1_label_a.next_to(vec_a_val + diag_offset, UP * 0.2)

        scene1_label_b = MathTex(r"\vec{b}", color=PURPLE_COLOR).scale(0.9)
        scene1_label_b.next_to(vec_b_val + diag_offset, DOWN * 0.4 + RIGHT * 0.1)

        proxy_b_target = Line(ORIGIN, vec_b_val).shift(diag_offset)
        proxy_a_target = Line(ORIGIN, vec_a_val).shift(diag_offset)
        target_angle = Angle(proxy_b_target, proxy_a_target, radius=0.7, color=BLUE_COLOR)
        
        scene1_angle_label = MathTex(r"\theta", color=BLUE_COLOR).scale(0.8)
        scene1_angle_label.next_to(target_angle, RIGHT, buff=0.1).shift(UP * 0.1)

        target_shadow_glow = create_hazy_line(
            start_pt=diag_offset,
            end_pt=target_proj_point,
            color=PINK_COLOR,
            core_width=0.05,
            glow_radius=0.40,
            num_layers=30,
            opacity=1.0
        )
        target_shadow_glow.set_z_index(-1)

        target_proj_line = DashedLine(vec_a_val + diag_offset, target_proj_point, color=GRAY)

        stack_a = MathTex(r"\begin{pmatrix} a_x \\ a_y \\ a_z \end{pmatrix}", color=PINK_COLOR).scale(0.85)
        stack_b = MathTex(r"\begin{pmatrix} b_x \\ b_y \\ b_z \end{pmatrix}", color=PURPLE_COLOR).scale(0.85)
        dot_sym = MathTex(r"\cdot", color=WHITE).scale(1.2)
        
        stack_group = VGroup(stack_a, dot_sym, stack_b).arrange(RIGHT, buff=0.3)
        stack_group.move_to(LEFT * 5.2 + UP * 2.2)

        # Force the original shadow to the background right as the translation begins
        shadow_glow.set_z_index(-1)

        anim_8_dur = 1.383
        self.play(
            FadeOut(proj_line_2),
            FadeOut(shadow_glow_2),
            FadeOut(new_eq),
            FadeOut(new_comp_label_ab),
            FadeOut(new_comp_label_ba),
            FadeOut(unit_x),
            FadeOut(unit_y),
            FadeOut(label_x),
            FadeOut(label_y),
            FadeOut(xy_dot_eq),
            FadeOut(xx_dot_eq),
            FadeOut(one_eq),
            FadeOut(new_angle_label),
            
            vec_a.animate.shift(diag_offset),
            vec_b.animate.shift(diag_offset),
            ReplacementTransform(proj_line, target_proj_line),
            ReplacementTransform(shadow_glow, target_shadow_glow),
            angle.animate.shift(diag_offset),
            
            ReplacementTransform(full_label_a, stack_a),
            ReplacementTransform(full_label_b, stack_b),
            
            FadeIn(scene1_angle_label),
            FadeIn(dot_sym),
            FadeIn(scene1_label_a),
            FadeIn(scene1_label_b),
            
            run_time=anim_8_dur
        )

        # ----------------------------------------------------
        # Event 9: 03:56:23 -> t = 236.383s
        # ----------------------------------------------------
        time_after_event_8 = 235.000 + anim_8_dur
        wait_9 = max(0, 236.383 - time_after_event_8)
        if wait_9 > 0:
            self.wait(wait_9)

        eq_dot_expanded = MathTex(
            r"=", 
            r"(", 
            r"a_x \hat{x}", 
            r"+", 
            r"a_y \hat{y}", 
            r"+", 
            r"a_z \hat{z}", 
            r")",
            r"\cdot", 
            r"(", 
            r"b_x \hat{x}", 
            r"+", 
            r"b_y \hat{y}", 
            r"+", 
            r"b_z \hat{z}", 
            r")",
            color=WHITE
        ).scale(0.85)
        eq_dot_expanded.next_to(stack_group, DOWN, buff=0.5).align_to(stack_group, LEFT)

        anim_9_dur = 1.5
        self.play(
            Write(eq_dot_expanded),
            run_time=anim_9_dur
        )

        eq_bottom_full = MathTex(
            r"=", 
            r"a_x b_x", 
            r"+ 0", 
            r"+ 0", 
            r"+ 0", 
            r"+ a_y b_y", 
            r"+ 0", 
            r"+ 0", 
            r"+ 0", 
            r"+ a_z b_z", 
            color=WHITE
        ).scale(0.85)
        eq_bottom_full.next_to(eq_dot_expanded, DOWN, buff=0.3).align_to(eq_dot_expanded, LEFT)

        # ----------------------------------------------------
        # Event 10: 04:02:17 -> t = 242.283s
        # ----------------------------------------------------
        time_after_event_9 = 236.383 + anim_9_dur
        wait_10 = max(0, 242.283 - time_after_event_9)
        if wait_10 > 0:
            self.wait(wait_10)

        eq_dot_expanded[2].set_color(PINK_COLOR)
        eq_dot_expanded[10].set_color(PURPLE_COLOR)

        anim_10_dur = 0.5
        self.play(
            Write(eq_bottom_full[0:2]),
            run_time=anim_10_dur
        )

        # ----------------------------------------------------
        # Event 11: 04:03:23 -> t = 243.383s
        # ----------------------------------------------------
        time_after_event_10 = 242.283 + anim_10_dur
        wait_11 = max(0, 243.383 - time_after_event_10)
        if wait_11 > 0:
            self.wait(wait_11)

        eq_dot_expanded[10].set_color(WHITE)
        eq_dot_expanded[12].set_color(PURPLE_COLOR)

        anim_11_dur = 0.4
        self.play(
            Write(eq_bottom_full[2]),
            run_time=anim_11_dur
        )

        # ----------------------------------------------------
        # Event 12: 04:04:18 -> t = 244.300s
        # ----------------------------------------------------
        time_after_event_11 = 243.383 + anim_11_dur
        wait_12 = max(0, 244.300 - time_after_event_11)
        if wait_12 > 0:
            self.wait(wait_12)

        eq_dot_expanded[12].set_color(WHITE)
        eq_dot_expanded[14].set_color(PURPLE_COLOR)

        anim_12_dur = 0.2
        self.play(
            Write(eq_bottom_full[3]),
            run_time=anim_12_dur
        )

        # ----------------------------------------------------
        # Event 13: 04:05:12 -> t = 245.200s
        # ----------------------------------------------------
        time_after_event_12 = 244.300 + anim_12_dur
        wait_13 = max(0, 245.200 - time_after_event_12)
        if wait_13 > 0:
            self.wait(wait_13)

        eq_dot_expanded[2].set_color(WHITE)
        eq_dot_expanded[14].set_color(WHITE)
        
        eq_dot_expanded[4].set_color(PINK_COLOR)
        eq_dot_expanded[10].set_color(PURPLE_COLOR)

        anim_13_dur = 0.4
        self.play(
            Write(eq_bottom_full[4]),
            run_time=anim_13_dur
        )

        # ----------------------------------------------------
        # Event 14: 04:06:14 -> t = 246.233s
        # ----------------------------------------------------
        time_after_event_13 = 245.200 + anim_13_dur
        wait_14 = max(0, 246.233 - time_after_event_13)
        if wait_14 > 0:
            self.wait(wait_14)

        eq_dot_expanded[10].set_color(WHITE)
        eq_dot_expanded[12].set_color(PURPLE_COLOR)

        anim_14_dur = 0.4
        self.play(
            Write(eq_bottom_full[5]),
            run_time=anim_14_dur
        )

        # ----------------------------------------------------
        # Event 15: 04:08:00 -> t = 248.000s
        # ----------------------------------------------------
        time_after_event_14 = 246.233 + anim_14_dur
        wait_15 = max(0, 248.000 - time_after_event_14)
        if wait_15 > 0:
            self.wait(wait_15)

        eq_dot_expanded[12].set_color(WHITE)
        eq_dot_expanded[14].set_color(PURPLE_COLOR)

        anim_15_dur = 0.2
        self.play(
            Write(eq_bottom_full[6]),
            run_time=anim_15_dur
        )

        # ----------------------------------------------------
        # Event 16: 04:08:18 -> t = 248.300s
        # ----------------------------------------------------
        time_after_event_15 = 248.000 + anim_15_dur
        wait_16 = max(0, 248.300 - time_after_event_15)
        if wait_16 > 0:
            self.wait(wait_16)

        eq_dot_expanded[4].set_color(WHITE)
        eq_dot_expanded[14].set_color(WHITE)
        
        eq_dot_expanded[6].set_color(PINK_COLOR)
        eq_dot_expanded[10].set_color(PURPLE_COLOR)

        anim_16_dur = 0.15
        self.play(
            Write(eq_bottom_full[7]),
            run_time=anim_16_dur
        )

        # ----------------------------------------------------
        # Event 17: 04:09:08 -> t = 249.133s
        # ----------------------------------------------------
        time_after_event_16 = 248.300 + anim_16_dur
        wait_17 = max(0, 249.133 - time_after_event_16)
        if wait_17 > 0:
            self.wait(wait_17)

        eq_dot_expanded[10].set_color(WHITE)
        eq_dot_expanded[12].set_color(PURPLE_COLOR)

        anim_17_dur = 0.2
        self.play(
            Write(eq_bottom_full[8]),
            run_time=anim_17_dur
        )

        # ----------------------------------------------------
        # Event 18: 04:10:09 -> t = 250.150s
        # ----------------------------------------------------
        time_after_event_17 = 249.133 + anim_17_dur
        wait_18 = max(0, 250.150 - time_after_event_17)
        if wait_18 > 0:
            self.wait(wait_18)

        eq_dot_expanded[12].set_color(WHITE)
        eq_dot_expanded[14].set_color(PURPLE_COLOR)

        anim_18_dur = 0.5
        self.play(
            Write(eq_bottom_full[9]),
            run_time=anim_18_dur
        )

        # ----------------------------------------------------
        # Event 19: 04:11:14 -> t = 251.233s
        # ----------------------------------------------------
        time_after_event_18 = 250.150 + anim_18_dur
        wait_19 = max(0, 251.233 - time_after_event_18)
        if wait_19 > 0:
            self.wait(wait_19)

        new_first_line = MathTex(r"\vec{a} \cdot \vec{b}", color=WHITE).scale(0.85)
        new_first_line.move_to(eq_dot_expanded.get_left(), aligned_edge=LEFT)

        compressed_bottom = MathTex(r"=", r"a_x b_x", r"+ a_y b_y", r"+ a_z b_z", color=WHITE).scale(0.85)
        shift_vec = eq_bottom_full[0].get_center() - compressed_bottom[0].get_center()
        compressed_bottom.shift(shift_vec)
        
        anim_19_dur = 1.5
        self.play(
            FadeOut(eq_bottom_full[2:5]),
            FadeOut(eq_bottom_full[6:9]),
            ReplacementTransform(eq_dot_expanded, new_first_line),
            ReplacementTransform(eq_bottom_full[0], compressed_bottom[0]),
            ReplacementTransform(eq_bottom_full[1], compressed_bottom[1]),
            ReplacementTransform(eq_bottom_full[5], compressed_bottom[2]),
            ReplacementTransform(eq_bottom_full[9], compressed_bottom[3]),
            run_time=anim_19_dur
        )

        # ----------------------------------------------------
        # Event 20: 04:14:04 -> t = 254.067s
        # ----------------------------------------------------
        time_after_event_19 = 251.233 + anim_19_dur
        wait_20 = max(0, 254.067 - time_after_event_19)
        if wait_20 > 0:
            self.wait(wait_20)

        scene1_top_eq = MathTex(
            r"\vec{a} \cdot \vec{b}",
            r"= a b \cos\theta",
            r"=",
            r"a_x b_x",
            r"+ a_y b_y",
            r"+ a_z b_z",
            color=WHITE
        ).scale(0.85).move_to(LEFT * 3.2 + UP * 2.2)

        anim_20_dur = 2.0
        self.play(
            FadeOut(stack_group),
            ReplacementTransform(new_first_line, scene1_top_eq[0]),
            ReplacementTransform(compressed_bottom[0], scene1_top_eq[2]),
            ReplacementTransform(compressed_bottom[1], scene1_top_eq[3]),
            ReplacementTransform(compressed_bottom[2], scene1_top_eq[4]),
            ReplacementTransform(compressed_bottom[3], scene1_top_eq[5]),
            FadeIn(scene1_top_eq[1]),
            run_time=anim_20_dur
        )

        # ----------------------------------------------------
        # Video-Editing Tail
        # ----------------------------------------------------
        self.wait(10.0)
        
        

        
if __name__ == "__main__":
    EXPORT_FINAL = True


    # Options: "all" or specific scene name(s) like "Scene2" or ["Scene1", "Scene2"]
    scenes_to_run = "Scene16"

    export_path = Path(r"C:\Users\ambri\Downloads\A Little Fizzy\Ep1 Dot Product to Geo\Scenes")

    scene_map = {
        "Scene1": Scene1,
        "Scene2": Scene2,
        "Scene3": Scene3,
        "Scene4": Scene4,
        "Scene5": Scene5,
        "Scene6": Scene6,
        "Scene7": Scene7,
        "Scene8": Scene8,
        "Scene9": Scene9,
        "BivectorTest": BivectorTest,
        "Scene10": Scene10,
        "Scene11": Scene11,
        "Scene12": Scene12,
        "Scene13": Scene13,
        "Scene14": Scene14,
        "Scene15": Scene15,
        "Scene16": Scene16,
        "Scene17": Scene17,
        "Scene18": Scene18,
        "Scene19": Scene19,
        "Scene20": Scene20,
        "Scene21": Scene21,
        "Scene22": Scene22,
        "Scene23": Scene23,
        "Scene24": Scene24,
    }

    # Resolve scene selection
    if scenes_to_run == "all":
        target_scenes = list(scene_map.keys())
    elif isinstance(scenes_to_run, list):
        target_scenes = scenes_to_runt
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