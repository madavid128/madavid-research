require 'liquid'
require 'date'

module Jekyll
  module GallerySortFilters
    YEAR_FROM_FILENAME = /-(19\d{2}|20\d{2})(?=\.[^.]+$)/.freeze

    def gallery_sort(items, descending = true)
      return items unless items.is_a?(Array)

      sorted = items.sort_by do |item|
        next [0, 0, ""] unless item.is_a?(Hash)

        year = _gallery_year(item)
        date_key = _gallery_date_key(item)
        title = (item["title"] || "").to_s

        [year, date_key, title]
      end

      descending ? sorted.reverse : sorted
    end

    private

    def _gallery_year(item)
      explicit = item["year"]
      if explicit
        y = explicit.to_s.strip
        return y.to_i if y.match?(/\A\d{4}\z/)
      end

      image = (item["image"] || "").to_s
      if (m = image.match(YEAR_FROM_FILENAME))
        return m[1].to_i
      end

      # If no year is present in either an explicit field or the filename,
      # treat the year as unknown (0). This keeps ordering driven by the year
      # suffix convention in filenames (e.g., `photo-2021.jpg`) rather than the
      # YAML `date` field (which often reflects when the site was updated).
      0
    end

    def _gallery_date_key(item)
      date_val = item["date"]
      if date_val.respond_to?(:to_time)
        return date_val.to_time.to_i
      end

      begin
        return Date.parse(date_val.to_s).to_time.to_i if date_val
      rescue StandardError
        # ignore
      end

      0
    end
  end
end

Liquid::Template.register_filter(Jekyll::GallerySortFilters)
