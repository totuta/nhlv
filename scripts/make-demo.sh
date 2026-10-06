#!/bin/zsh
set -e

root="${0:A:h:h}"
frames="$root/assets/demo-frames"
font="/System/Library/Fonts/Supplemental/Andale Mono.ttf"
logo="$root/assets/nhlv-logo.png"

mkdir -p "$frames"
rm -f "$frames"/*.png(N) "$root/assets/nhlv-demo-v2.gif"

render() {
  local frame="$1"
  shift
  magick -size 1100x620 xc:'#050b14' \
    -fill none -stroke '#17304f' -strokewidth 2 \
    -draw 'roundrectangle 35,35 1065,585 18,18' \
    -fill '#88a7c4' -stroke none -font "$font" -pointsize 27 \
    -draw "text 70,92 'nhlv  /  terminal hockey'" \
    -fill '#35d0ff' -pointsize 22 -draw "text 70,132 '────────────────────────────────────────────────────────'" \
    -fill '#d9e7f5' -pointsize 25 "$@" \
    "$frames/$frame.png"
  magick "$frames/$frame.png" \( "$logo" -resize 145x145 \) -geometry +875+58 -composite "$frames/$frame.png"
}

render 01 -fill '#d9e7f5' -draw "text 70,205 '$ nhlv scores --team MTL'"
render 02 -fill '#7ee7ff' -draw "text 70,205 '$ nhlv scores --team MTL'" -fill '#d9e7f5' -draw "text 70,270 'NHL Scores: 2026-10-05'"
render 03 -fill '#7ee7ff' -draw "text 70,205 '$ nhlv scores --team MTL'" -fill '#d9e7f5' -draw "text 70,270 'NHL Scores: 2026-10-05'" -draw "text 70,325 '18:00  MTL  4  @  TOR  2  FINAL'" -fill '#ff8e9e' -draw "text 70,380 '20:30  EDM  3  @  VAN  1  FINAL'"
render 04 -fill '#d9e7f5' -draw "text 70,205 '$ nhlv standings'" -fill '#7ee7ff' -draw "text 70,270 'NHL Standings'" -fill '#d9e7f5' -draw "text 70,325 'Atlantic'" -draw "text 70,370 'RK  TEAM                         GP  W  L  OT  PTS'" -draw "text 70,415 ' 1   Montreal Canadiens           5  4  1   0    8'" -draw "text 70,460 ' 2   Toronto Maple Leafs          5  3  1   1    7'" -draw "text 70,505 ' 3   Ottawa Senators              5  2  2   1    5'"
render 05 -fill '#d9e7f5' -draw "text 70,205 '$ nhlv favorite-stats'" -fill '#7ee7ff' -draw "text 70,270 'NHL Favourite Player Stats'" -fill '#d9e7f5' -draw "text 70,325 'Skaters'" -draw "text 70,380 'MTL  L. Hutson                 1  2  3  +2  4  0  22:10'"
render 06 -fill '#d9e7f5' -draw "text 70,205 '$ nhlv schedule'" -fill '#7ee7ff' -draw "text 70,270 'NHL Schedule'" -fill '#d9e7f5' -draw "text 70,325 '2026-10-06'" -draw "text 70,380 '19:00  MTL  @  OTT  FUT'"

magick -delay 220 -loop 0 "$frames"/*.png "$root/assets/nhlv-demo-v2.gif"
