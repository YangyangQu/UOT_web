# generate_html_table.py
import os

# 假设你的文件名格式是规范的，例如：
# 1. source:  {id}_src.wav
# 2. target:  {id}_ref.wav
# 3. baseline: {id}_knn.wav
# 4. ours:     {id}_ours.wav

sample_ids = ["001", "002", "003"] # 你的样本ID列表

print("<tbody>")
for sid in sample_ids:
    html = f"""
    <tr>
        <td>
            <audio controls src="samples/sample{sid}_src.wav"></audio>
            <div class="desc">Source</div>
        </td>
        <td>
            <audio controls src="samples/sample{sid}_ref.wav"></audio>
            <div class="desc">Target</div>
        </td>
        <td><audio controls src="samples/sample{sid}_knn.wav"></audio></td>
        <td><audio controls src="samples/sample{sid}_freevc.wav"></audio></td>
        <td><audio controls src="samples/sample{sid}_ours.wav"></audio></td>
    </tr>
    """
    print(html)
print("</tbody>")