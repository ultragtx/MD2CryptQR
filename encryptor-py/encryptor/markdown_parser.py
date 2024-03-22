import re
import json

class MarkdownParser:

    NO_TITLE = ""

    def __init__(self, input_file, compact_mode, max_qr_data_length=800):
        self.input_file = input_file
        self.compact_mode = compact_mode
        self.max_qr_data_length = max_qr_data_length  # Maximum characters that can be stored in a single QR code

    def _get_other_json_parts_byte_length(self, title, idx):
        chunk = {
            "title": title,
            "idx": idx,
            "content": ""
        }
        json_str = json.dumps(chunk, ensure_ascii=False)
        return len(json_str.encode('utf-8'))

    def _split_large_section(self, title, content):
        parts = []
        current_part = ""
        current_length = 0
        first_time = True

        for line in content.split("\n"):
            line_bytes = line.encode('utf-8')
            line_length = len(line_bytes) + 1  # +1 for the newline character

            # Calculate JSON byte length of extra content
            json_length = self._get_other_json_parts_byte_length(title, self.idx)

            if json_length + current_length + line_length > self.max_qr_data_length:
                # If including the current line exceeds the limit, append the current part
                parts.append({
                    "title": title if first_time else "",
                    "idx": self.idx,
                    "content": current_part
                })
                first_time = False

                current_part = ""
                current_length = 0
                self.idx += 1

            current_part += line + "\n"
            current_length += line_length

        if current_part:
            parts.append({
                "title": title if first_time else "",
                "idx": self.idx,
                "content": current_part
            })

            self.idx += 1

        return parts

        # parts = []
        # current_part = ""
        # for line in content.split("\n"):
        #     if len(current_part) + len(line) + 1 > self.max_qr_data_length:
        #         parts.append(current_part)
        #         current_part = ""
        #     current_part += line + "\n"
        # if current_part:
        #     parts.append(current_part)
        # return parts

    def parse_markdown(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regular expression to match Markdown headers, from `# Title` to `###### Title`
        if self.compact_mode:
            sections = [content]
        else:
            sections = re.split(r'(^#{1,6} .+)', content, flags=re.M)[1:]

        section_list = [] # List of sections, each a list of chunks
        self.idx = 0 # global idx

        # print('--=--------------')
        # print(len(sections))
        # print(sections[0])
        # print('-')
        # print(sections[1])

        current_title = self.NO_TITLE
        
        for section in sections:
            # Skip empty strings
            if not section.strip():
                continue

            if self.compact_mode:
                content_parts = self._split_large_section(current_title, section.strip())
                section_list.append(content_parts)
            else:
                # Check if the section is a title
                if re.match(r'^#{1,6} .+', section):
                    current_title = section.strip()
                else:  # This is content
                    content_parts = self._split_large_section(current_title, section.strip())
                    section_list.append(content_parts)

        return section_list
