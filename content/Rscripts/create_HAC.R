



plot_cumulative_avg_gain <- function(table_path) {
  library(forcats)
  library(dplyr)
  library(ggplot2)
  library(ggrepel)
  
  tracktablecrossings <- read.csv(table_path)
  

  tracktablecrossings$rank_total_upstr_hab[tracktablecrossings$rank_total_upstr_hab == ""] <- NA
  tracktablecrossings <- tracktablecrossings[!is.na(tracktablecrossings$rank_total_upstr_hab), ]

  # sort + cumulative on FULL ranked list (system-wide basis)
  tracktablecrossings <- tracktablecrossings %>%
    arrange(desc(avg_gain_per_barrier)) %>%
    mutate(cum_avg_gain = cumsum(avg_gain_per_barrier))

  # system-wide 50% (all ranked barriers)
  total_system <- max(tracktablecrossings$cum_avg_gain, na.rm = TRUE)
  target_y <- 0.5 * total_system

  mid_pt_all <- tracktablecrossings %>%
    mutate(x_idx_all = seq_along(cum_avg_gain)) %>%
    slice(which.min(abs(cum_avg_gain - target_y)))

  x1 <- mid_pt_all$x_idx_all
  y1 <- target_y

  # HAC subset based on include_in_hac but don't split sets 
  tracktablecrossings_hac <- tracktablecrossings %>%
    mutate(
      include_clean = tolower(trimws(include_in_hac)),
      label_clean   = tolower(trimws(label_in_hac))
    ) %>%
    group_by(rank_avg_gain_per_barrier) %>%
    mutate(
      any_yes_in_set = any(include_clean == "yes", na.rm = TRUE),
      keep_in_hac = (include_clean == "yes") | (n() > 1 & any_yes_in_set)
    ) %>%
    ungroup() %>%
    filter(keep_in_hac)

  # Nick L's requested legend order
  status_levels <- c(
    "Rehabilitated Barrier",
    "Non-actionable Barrier",
    "Priority Barrier",
    "Data-deficient Barrier",
    "Unassessed Structure"
  )

  df <- tracktablecrossings_hac %>%
    mutate(
      x_idx = seq_along(cum_avg_gain),
      
      status_clean = trimws(structure_list_status),
      next_clean   = tolower(trimws(next_steps)),
      
      symbol_cat = case_when(
        status_clean == "Rehabilitated barrier" ~ "Rehabilitated Barrier",
        status_clean == "Confirmed barrier" & next_clean == "non-actionable" ~ "Non-actionable Barrier",
        status_clean == "Confirmed barrier" & next_clean != "non-actionable" ~ "Priority Barrier",
        status_clean == "Assessed structure that remains data deficient" ~ "Data-deficient Barrier",
        status_clean == "" ~ "Unassessed Structure",
        TRUE ~ "Other"
      ),
      
      symbol_cat = factor(symbol_cat, levels = status_levels),
      
      # label rules:
      # - only label if include_in_hac == yes AND label_in_hac == yes
      # - then internal_name, else barrier_id
      label_pt = case_when(
        include_clean == "yes" & label_clean == "yes" &
          !is.na(internal_name) & trimws(internal_name) != "" ~ trimws(internal_name),
        
        include_clean == "yes" & label_clean == "yes" &
          (is.na(internal_name) | trimws(internal_name) == "") &
          !is.na(barrier_id) & trimws(barrier_id) != "" ~ trimws(barrier_id),
        
        TRUE ~ NA_character_
      )
    ) %>%
    arrange(x_idx)

  # alternate labels go up vs down for less overlap hopefully...
  df <- df %>%
    mutate(
      has_label = !is.na(label_pt) & trimws(label_pt) != ""
    ) %>%
    mutate(
      lab_group = ifelse(has_label, cumsum(has_label), NA_integer_),
      lab_side = ifelse(has_label & (lab_group %% 2 == 0), "down",
                        ifelse(has_label, "up", NA_character_))
    )

  df_up <- df %>% filter(lab_side == "up")
  df_down <- df %>% filter(lab_side == "down")

  # extend curve to (0,0) as Betty has done in her HACs (it looks nicer)
  df_line <- bind_rows(
    tibble(x_idx = 0, cum_avg_gain = 0, rank_avg_gain_per_barrier = NA_real_),
    df %>% select(x_idx, cum_avg_gain, rank_avg_gain_per_barrier)
  )

  # segments for cumulative curve + set highlighting
  df_seg <- df_line %>%
    mutate(
      xend = lead(x_idx),
      yend = lead(cum_avg_gain),
      is_set_seg = !is.na(rank_avg_gain_per_barrier) &
        rank_avg_gain_per_barrier == lead(rank_avg_gain_per_barrier)
    ) %>%
    filter(!is.na(xend))

  has_sets <- any(df_seg$is_set_seg, na.rm = TRUE)

  # show 50% only if it falls within plotted y-range
  max_y_plot <- max(df$cum_avg_gain, na.rm = TRUE)
  show_50 <- is.finite(y1) && (y1 <= max_y_plot)
  x1_plot <- min(x1, max(df$x_idx, na.rm = TRUE))

  line_breaks <- c() # line legend logic here
  if (has_sets) line_breaks <- c(line_breaks, "Set segment (tied rank)")
  if (show_50)  line_breaks <- c(line_breaks, "50% of system-wide habitat blocked")

  legend_set <- tibble(x = -1, xend = -0.5, y = 0, yend = 0, line_lab = "Set segment (tied rank)")
  legend_50  <- tibble(x = -1, xend = -0.5, y = 0, yend = 0, line_lab = "50% of system-wide habitat blocked")

  set.seed(1)

  p <- ggplot(df_line, aes(x_idx, cum_avg_gain)) +
    
    # main curve (behind points)
    geom_segment(
      data = df_seg,
      aes(x = x_idx, y = cum_avg_gain, xend = xend, yend = yend),
      color = "black",
      linewidth = 0.7,
      lineend = "round",
      linejoin = "round"
    )

  if (has_sets) {
    p <- p +
      geom_segment(
        data = filter(df_seg, is_set_seg),
        aes(x = x_idx, y = cum_avg_gain, xend = xend, yend = yend),
        color = "grey90",
        linewidth = 1.2,
        lineend = "round",
        linejoin = "round"
      )
  }

  if (show_50) {
    p <- p +
      annotate("segment",
              x = 0, xend = x1_plot, y = y1, yend = y1,
              linetype = "dashed", linewidth = 0.6, color = "black", lineend = "round"
      ) +
      annotate("segment",
              x = x1_plot, xend = x1_plot, y = 0, yend = y1,
              linetype = "dashed", linewidth = 0.6, color = "black", lineend = "round"
      )
  }

  # more legend-key layers logic 
  if (length(line_breaks) > 0) {
    
    if (has_sets) {
      p <- p +
        geom_segment(
          data = legend_set,
          aes(x = x, y = y, xend = xend, yend = yend, linetype = line_lab),
          inherit.aes = FALSE,
          color = "grey90",
          linewidth = 1.2,
          lineend = "round"
        )
    }
    
    if (show_50) {
      p <- p +
        geom_segment(
          data = legend_50,
          aes(x = x, y = y, xend = xend, yend = yend, linetype = line_lab),
          inherit.aes = FALSE,
          color = "black",
          linewidth = 0.6,
          lineend = "round"
        )
    }
    
    p <- p +
      scale_linetype_manual(
        name = NULL,
        values = c(
          "Set segment (tied rank)" = "solid",
          "50% of system-wide habitat blocked" = "dashed"
        ),
        breaks = line_breaks
      ) +
      guides(
        fill = guide_legend(order = 1),
        color = guide_legend(order = 1),
        linetype = guide_legend(order = 2)
      )
  }

  # points on top (rounded stroke)
  p <- p +
    geom_point(
      data = df,
      aes(fill = symbol_cat, color = symbol_cat),
      shape = 21,
      size = 2.8,
      stroke = 1.5
    )

  # labels split above and below to reduce overlap
  p <- p +
    geom_text_repel(
      data = df_up,
      aes(label = label_pt),
      na.rm = TRUE,
      size = 2,
      direction = "y",
      nudge_y = 14,
      force = 5,
      box.padding = 0.7,
      point.padding = 0.8,
      min.segment.length = 0,
      segment.color = "grey40",
      segment.size = 0.35,
      max.overlaps = Inf
    ) +
    geom_text_repel(
      data = df_down,
      aes(label = label_pt),
      na.rm = TRUE,
      size = 2,
      direction = "y",
      nudge_y = -14,
      force = 5,
      box.padding = 0.7,
      point.padding = 0.8,
      min.segment.length = 0,
      segment.color = "grey40",
      segment.size = 0.35,
      max.overlaps = Inf
    )

  p +
    scale_fill_manual(
      name = "Structure Status",
      breaks = status_levels,
      drop = TRUE,
      values = c(
        "Rehabilitated Barrier" = "turquoise",
        "Non-actionable Barrier" = "red1",
        "Priority Barrier" = "red1",
        "Data-deficient Barrier" = "red1",
        "Unassessed Structure" = "purple"
      )
    ) +
    scale_color_manual(
      name = "Structure Status",
      breaks = status_levels,
      drop = TRUE,
      values = c(
        "Rehabilitated Barrier" = "green4",
        "Non-actionable Barrier" = "red1",
        "Priority Barrier" = "gold1",
        "Data-deficient Barrier" = "pink1",
        "Unassessed Structure" = "purple"
      )
    ) +
    scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.10))) +
    scale_x_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.02))) +
    labs(
      x = "Structure count ordered by model rank",
      y = "Cumulative habitat upstream of structures (km)"
    ) +
    theme_minimal() +
    theme(
      panel.grid = element_blank(),
      axis.text  = element_text(color = "black"),
      axis.title = element_text(color = "black"),
      axis.line = element_line(color = "black", linewidth = 0.8),
      axis.ticks = element_line(color = "black"),
      axis.ticks.length = unit(3, "pt"),
      plot.margin = margin(12, 10, 12, 12)
    )
  ggsave("content/images/hac-lnic-test.png", width = 10, height = 6, units = "in")
  }