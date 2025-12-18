#!/usr/bin/env ruby
# frozen_string_literal: true

require "yaml"

ROOT = File.expand_path("..", __dir__)

def load_front_matter(path)
  text = File.read(path)
  parts = text.split(/^---\s*$\n/)
  return {} if parts.length < 3
  YAML.safe_load(parts[1]) || {}
end

def normalize_name(name)
  name.to_s.strip.downcase.gsub(/\s+/, " ")
end

citations_path = File.join(ROOT, "_data", "citations.yaml")
member_path = File.join(ROOT, "_members", "michael-david.md")
out_path = File.join(ROOT, "_data", "collaborators.generated.yaml")

unless File.exist?(citations_path)
  warn "Missing #{citations_path}"
  exit(1)
end

citations = YAML.safe_load(File.read(citations_path)) || []

self_data = File.exist?(member_path) ? load_front_matter(member_path) : {}
self_names = []
self_names << self_data["name"] if self_data["name"]
self_names.concat(self_data["aliases"]) if self_data["aliases"].is_a?(Array)
self_names = self_names.compact.map { |n| normalize_name(n) }.uniq

counts = Hash.new(0)

citations.each do |citation|
  next unless citation.is_a?(Hash)
  authors = citation["authors"]
  next unless authors.is_a?(Array)

  authors.each do |author|
    name = author.to_s.strip
    next if name.empty?
    next if self_names.include?(normalize_name(name))
    counts[name] += 1
  end
end

generated = counts
  .sort_by { |name, count| [-count, name.downcase] }
  .map do |name, count|
    {
      "name" => name,
      "status" => "current",
      "institution" => "",
      "city" => "",
      "country" => "",
      "lat" => nil,
      "lon" => nil,
      "link" => "",
      "tags" => ["collaboration"],
      "papers" => count,
    }
  end

File.write(out_path, generated.to_yaml)
puts "Wrote #{out_path} (#{generated.length} people)."
puts "Next: copy entries you want into _data/collaborators.yaml and fill in city/country + lat/lon."

