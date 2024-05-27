import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st


def latex_to_svg(latex_code: str):
    plt.rcParams["mathtext.fontset"] = "cm"
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex_code}$", fontsize=12)

    output = BytesIO()
    fig.savefig(
        output,
        dpi=400,
        transparent=True,
        format="svg",
        bbox_inches="tight",
        pad_inches=0.0,
    )
    plt.close(fig)

    output.seek(0)
    return output.read().decode("utf-8")


def run_latexmk(input_file: str, output_dir: str):
    subprocess.run(["latexmk", f"-outdir={output_dir}", input_file], check=True)
    subprocess.run(
        ["pdfcrop", f"{output_dir}/tex.pdf", f"{output_dir}/tex.pdf"], check=True
    )


def convert_pdf_to_svg(pdf_file: Path, svg_file: Path):
    subprocess.run(["pdf2svg", pdf_file, svg_file], check=True)


st.title("TeX to PDF/SVG")

latex_type = st.radio("LaTeX Type", ("Snippet", "Full LaTeX Document"))

if latex_type == "Snippet":
    if latex_input := st.text_area(
        "Enter LaTeX Snippet:",
        value=r"\frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}",
    ):
        svg_data = latex_to_svg(f"{latex_input}")
        st.image(svg_data, use_column_width=True)

elif latex_input := st.text_area(
    "Enter Full LaTeX Document:",
    value="""\\documentclass[a4paper,11pt,oneside,uplatex]{jsarticle}
\\usepackage[margin=1in]{geometry}
\\usepackage{siunitx}
\\usepackage{amsmath}
\\pagestyle{empty}
\\begin{document}

$f_a = \sum_{(p,q) \in C} f_{apq}$

\end{document}""",
    height=400,
):
    output_dir = "out"
    output_pdf_file = Path(output_dir) / "tex.pdf"
    output_svg_file = Path(output_dir) / "tex.svg"

    input_tex_file = "tex.tex"
    with open(input_tex_file, "w") as file:
        file.write(latex_input)

    generate_pdf = st.checkbox("Generate PDF", value=True)
    generate_svg = st.checkbox("Generate SVG")

    if st.button("Generate"):
        if generate_pdf:
            run_latexmk(input_tex_file, output_dir)
            desktop_path = Path.home() / "Desktop"
            desktop_pdf_path = desktop_path / "tex.pdf"
            shutil.copy(output_pdf_file, desktop_pdf_path)
            st.success("PDF file generated on your Desktop.")

        if generate_svg:
            convert_pdf_to_svg(output_pdf_file, output_svg_file)
            desktop_path = Path.home() / "Desktop"
            desktop_svg_path = desktop_path / "tex.svg"
            shutil.copy(output_svg_file, desktop_svg_path)
            st.success("SVG file generated on your Desktop.")
