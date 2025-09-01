#!/usr/bin/env Rscript

# Load the AMR library
if (!requireNamespace("AMR", quietly = TRUE)) {
  install.packages("AMR")
}
library(AMR)

# Read command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Check if an argument was provided
if (length(args) == 0) {
  stop("Please provide an organism name as an argument. Example: Rscript get_amr_code.R 'Streptococcus pneumoniae'", call. = FALSE)
}

# Take the first argument as the organism name
organism_name <- args[1]

# Convert the name to the AMR code
# The as.mo() function is the standard way to do this.
amr_code <- as.mo(organism_name)

# Print the AMR code
cat(amr_code)
cat("\n")