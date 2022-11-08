__author__ = "Leanne Whitmore"
__email__ = "leanne382@gmail.com"
__description__ = "Quantifies single cell viral reads"

# ----Libraries
import os
import argparse
import shutil
from scqv.map_reads import process_reads as pr
from scqv.map_reads import map_reads as mr
from scqv.process_10x import extract10x as ex
from scqv.quantify import viral_copies as vc
from scqv.quantify import viral_genes as vg
from scqv.quantify import integrate
from scqv.visualization import viz
from scqv.variantcalling import variantcalling as vcl


def parse_arguments():
    parser = argparse.ArgumentParser(prog="scViralQuant", description="Quantify sc viral mapping reads")
    parser.add_argument("-10x", "--path10x", type=str, required=True)
    parser.add_argument("-op", "--output_path", default="output_scviralquant")
    parser.add_argument("-p", "--processors", default=1)
    parser.add_argument("-p2genome", "--path2genome", type=str, required=True)
    parser.add_argument("-align", "--aligner", type=str, required=True, default="bbmap")
    parser.add_argument("-in_filtered", "--input_filtered_folder", type=str, required=False, default="filtered_feature_bc_matrix")
    parser.add_argument("-out_filtered", "--output_filtered_folder", type=str, required=False, default="filtered_feature_bc_matrix")
    parser.add_argument("-in_raw", "--input_raw_folder", type=str, required=False, default="raw_feature_bc_matrix")
    parser.add_argument("-out_raw", "--output_raw_folder", type=str, required=False, default="raw_feature_bc_matrix")
    parser.add_argument("-overwrite", "--overwrite_feature_matrix", required=False, action="store_true")
    parser.add_argument("--tmp_removal", required=False, action="store_true")
    parser.add_argument("--bbmap_params",  nargs="+")
    parser.add_argument("--bowtie2_params", nargs="+")

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    print(args.bbmap_params)
    viable_cb = ex.extract_viable_10x(args.path10x)
    pr.process_unmapped_reads(args, viable_cb)
    mr.map2viralgenome(args)
    dfvc, gene_name = vc.htseq_run(args)
    viz.generate_viral_copy_plots(args, gene_name, dfvc)
    integrate.integrate_data_2_matrix(args, dfvc, gene_name)
    dfgenes = vg.htseq_run(args)
    if dfgenes is not False:
        viz.generate_viral_gene_plots(args, dfgenes)
        integrate.integrate_viralgenes_data_2_matrix(args, dfgenes)
    if args.tmp_removal:
        shutil.rmtree(os.path.join(args.output_path,"_tmp"))
