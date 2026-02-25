library("flextable")
library("magrittr")
library("officer")

std_border <- fp_border(color = "grey")


# Table formatting for csv's
format_flextable <- function(ft) {
  ft <- ft %>%
    colformat_num(big.mark = "", decimal.mark = ".", digits = 2) %>%
    bg(bg = "#008270", part = "header") %>%
    color(color = "white", part = "header") %>%
    set_caption() %>%
    align_text_col(align = "left", header = TRUE) %>%
    align_nottext_col(align = "left", header = TRUE) %>%
    vline(part = "all", border = std_border) %>%
    hline(part = "all", border = std_border) %>%
    autofit()
  return(ft)
}