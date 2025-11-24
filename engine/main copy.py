from chart_section import ChartSection
import json

if __name__ == "__main__":
   chart_sections = []
   
   raglan = ChartSection(name="raglan", start_side="RS", sts = 23, rows = 21)
   raglan.cast_on_start(122)
   raglan.repeat_rounds(["repeat(k1, p1)"], 15)
   raglan.repeat_rounds(["repeat(k1)"], 30)
   raglan.place_marker("WS", 4)
   raglan.add_round("bo4, repeat(k1), rm").place_on_hold()
   raglan.add_round("repeat(k1)")
   raglan.repeat_rounds(
       ["k1, dec, repeat(k1), dec, k1",
        "repeat(k1)"]
    , 23)
   num_stitches = raglan.get_current_num_of_stitches()
   raglan.place_marker("RS", int(num_stitches/2) - 6)
   raglan.place_marker("RS", int(num_stitches/2) + 7)
   raglan.add_round("k1, dec, repeat(k1), sm, bo13, sm, repeat(k1), dec, k1")
   raglan.add_row("p26").place_on_hold()
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   stitches_on_hold = raglan.add_row("").place_on_hold()
   raglan.place_on_needle(stitches_on_hold, "WS")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")
   raglan.add_row("k1, dec, repeat(k1), dec, k1")
   raglan.add_row("repeat(p1)")

   raglan_back = ChartSection(name="raglan_back", start_side="RS", sts = 23, rows = 21)
   raglan_back.cast_on_start(122)
   raglan_back.repeat_rounds(["repeat(k1, p1)"], 15)
   raglan_back.repeat_rounds(["repeat(k1)"], 30)
   raglan_back.place_marker("WS", 2)
   raglan_back.add_round("bo4, repeat(k1), rm").place_on_hold()
   raglan_back.add_round("repeat(k1)")
   raglan_back.repeat_rounds(
       ["k1, dec, repeat(k1), dec, k1",
        "repeat(k1)"]
    , 31)
   
   
   sleeve = ChartSection(name="sleeve", start_side="RS", sts = 23, rows = 21)
   sleeve.cast_on_start(60)
   sleeve.repeat_rounds(["repeat(k1, p1)"], 15)
   sleeve.add_round(["repeat(k2, inc)"]).cast_on(1)
   sleeve.repeat_rounds(["repeat(k1)"], 96)
   sleeve.add_round("bo7, repeat(k1)")
   sleeve.repeat_rounds(["repeat(k1)"], 11)
   sleeve.repeat_rounds(["k1, dec, repeat(k1), dec, k1",
                         "repeat(k1)"], 26)

   chart_sections.append(raglan_back)
   chart_sections.append(raglan)
   chart_sections.append(sleeve)
   # chart_sections.append(right_front)
   # Convert the ChartSection object to a dictionary
   charts_data = {
        "charts": [
            {
                "name": chart.name,
                "nodes": chart.nodes,
                "links": chart.links
            }
            for chart in chart_sections
        ]
    }

    # Save individual chart files (optional - for backward compatibility)
   for chart in chart_sections:
        with open(f"{chart.name}.json", "w") as f:
            json.dump({
                "name": chart.name,
                "nodes": chart.nodes,
                "links": chart.links
            }, f, indent=2)

   # Save master charts file
   with open("charts.json", "w") as f:
        json.dump(charts_data, f, indent=2)

   print(f"Data written to charts.json with {len(chart_sections)} chart(s):")
   for chart in chart_sections:
        print(f"  - {chart.name}.json")


   print("Data written to left_back.json")