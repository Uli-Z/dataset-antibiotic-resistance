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
  stop("Please provide an antibiotic name as an argument. Example: Rscript get_antibiotic_amr_code.R 'Penicillin'", call. = FALSE)
}

# Take the first argument as the antibiotic name
antibiotic_name <- args[1]

# Convert the name to the AMR code
# The as.ab() function is the standard way to do this.
amr_code <- as.ab(antibiotic_name)

# Print the AMR code
cat(amr_code)
cat("\n")
