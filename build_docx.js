const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  LevelFormat, TableOfContents, PageBreak, BorderStyle,
} = require("docx");

const OUTPUT_DIR = path.join(__dirname, "output");
const OUT_FILE = path.join(__dirname, "CCNP_ENCOR_Summary_TH.docx");

const SECTION_TITLES = {
  "01": "Section 1: Enterprise LAN Architecture",
  "02": "Section 2: Enterprise Routing Network",
  "03": "Section 3: Virtualization Technologies",
  "04": "Section 4: Enterprise Wireless Architecture",
  "05": "Section 5: Network Services",
  "06": "Section 6: Enterprise Security Architecture",
  "07": "Section 7: Automation and Assurance",
  "08": "Section 8: Network Programmability",
};

// ---- inline markdown (bold / inline code) -> TextRun[] ----
function parseInline(text) {
  const runs = [];
  // split on **bold** and `code`
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let lastIndex = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > lastIndex) {
      runs.push(new TextRun({ text: text.slice(lastIndex, m.index), font: "Sarabun" }));
    }
    const token = m[0];
    if (token.startsWith("**")) {
      runs.push(new TextRun({ text: token.slice(2, -2), bold: true, font: "Sarabun" }));
    } else if (token.startsWith("`")) {
      runs.push(new TextRun({ text: token.slice(1, -1), font: "Consolas", size: 20 }));
    }
    lastIndex = re.lastIndex;
  }
  if (lastIndex < text.length) {
    runs.push(new TextRun({ text: text.slice(lastIndex), font: "Sarabun" }));
  }
  if (runs.length === 0) runs.push(new TextRun({ text: "", font: "Sarabun" }));
  return runs;
}

// ---- markdown body -> Paragraph[] ----
function parseMarkdownBody(md) {
  const lines = md.split("\n");
  const paragraphs = [];
  let i = 0;
  let inCode = false;
  let codeBuffer = [];

  function flushCode() {
    if (codeBuffer.length) {
      paragraphs.push(
        new Paragraph({
          children: [new TextRun({ text: codeBuffer.join("\n"), font: "Consolas", size: 19 })],
          shading: { fill: "F2F2F2" },
          spacing: { before: 80, after: 80 },
          border: {
            top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
            bottom: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
            left: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
            right: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
          },
        })
      );
      codeBuffer = [];
    }
  }

  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trimEnd();

    if (line.trim().startsWith("```")) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        inCode = true;
      }
      i++;
      continue;
    }
    if (inCode) {
      codeBuffer.push(raw);
      i++;
      continue;
    }

    if (line.trim() === "" ) { i++; continue; }
    if (line.trim() === "---") { i++; continue; } // skip hr

    // headings ### #### etc -> Heading3 (topic itself is Heading2)
    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const text = headingMatch[2].replace(/\*\*/g, "");
      paragraphs.push(
        new Paragraph({
          heading: level <= 3 ? HeadingLevel.HEADING_3 : HeadingLevel.HEADING_4,
          children: parseInline(text),
          spacing: { before: 200, after: 120 },
        })
      );
      i++;
      continue;
    }

    // bullet list: *   text  or -   text
    const bulletMatch = line.match(/^\s*[\*\-]\s+(.*)$/);
    if (bulletMatch) {
      paragraphs.push(
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: parseInline(bulletMatch[1]),
          spacing: { after: 60 },
        })
      );
      i++;
      continue;
    }

    // numbered list: 1.  text
    const numMatch = line.match(/^\s*\d+\.\s+(.*)$/);
    if (numMatch) {
      paragraphs.push(
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: parseInline(numMatch[1]),
          spacing: { after: 60 },
        })
      );
      i++;
      continue;
    }

    // normal paragraph
    paragraphs.push(
      new Paragraph({
        children: parseInline(line),
        spacing: { after: 100 },
        alignment: AlignmentType.LEFT,
      })
    );
    i++;
  }
  flushCode();
  return paragraphs;
}

function main() {
  const folders = fs
    .readdirSync(OUTPUT_DIR)
    .filter((f) => fs.statSync(path.join(OUTPUT_DIR, f)).isDirectory())
    .sort();

  const children = [];

  // ---- Cover page ----
  children.push(
    new Paragraph({
      children: [new TextRun({ text: "", font: "Sarabun" })],
      spacing: { before: 2000 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: "CCNP ENCOR 350-401",
          bold: true,
          size: 56,
          font: "Sarabun",
        }),
      ],
      spacing: { after: 300 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: "สรุปเนื้อหาภาษาไทย",
          bold: true,
          size: 40,
          font: "Sarabun",
        }),
      ],
      spacing: { after: 200 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: "รวบรวมจาก 68 หัวข้อ",
          size: 28,
          font: "Sarabun",
          color: "555555",
        }),
      ],
      spacing: { after: 100 },
    }),
    new Paragraph({ children: [new PageBreak()] })
  );

  // ---- Table of contents ----
  children.push(
    new Paragraph({
      children: [new TextRun({ text: "สารบัญ", bold: true, size: 36, font: "Sarabun" })],
      spacing: { after: 200 },
    }),
    new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }),
    new Paragraph({ children: [new PageBreak()] })
  );

  let currentSection = null;

  for (const folder of folders) {
    const mdPath = path.join(OUTPUT_DIR, folder, "summary_th.md");
    if (!fs.existsSync(mdPath)) {
      console.log(`SKIP (missing summary): ${folder}`);
      continue;
    }
    const sectionNum = folder.slice(0, 2);
    const sectionTitle = SECTION_TITLES[sectionNum] || `Section ${sectionNum}`;

    if (sectionTitle !== currentSection) {
      if (currentSection !== null) {
        children.push(new Paragraph({ children: [new PageBreak()] }));
      }
      children.push(
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun({ text: sectionTitle, font: "Sarabun" })],
          spacing: { before: 200, after: 200 },
        })
      );
      currentSection = sectionTitle;
    }

    const raw = fs.readFileSync(mdPath, "utf-8");
    const lines = raw.split("\n");
    let topicTitle = folder;
    let bodyStart = 0;
    if (lines[0] && lines[0].startsWith("# ")) {
      topicTitle = lines[0].slice(2).trim();
      bodyStart = 1;
    }
    const body = lines.slice(bodyStart).join("\n");

    children.push(
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun({ text: topicTitle, font: "Sarabun" })],
        spacing: { before: 240, after: 160 },
      })
    );
    children.push(...parseMarkdownBody(body));
    console.log(`Added: ${folder} -> ${topicTitle}`);
  }

  const doc = new Document({
    styles: {
      default: {
        document: { run: { font: "Sarabun", size: 22 } },
      },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 34, bold: true, font: "Sarabun", color: "1F4E79" },
          paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 },
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 28, bold: true, font: "Sarabun", color: "2E75B6" },
          paragraph: { spacing: { before: 200, after: 160 }, outlineLevel: 1 },
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: "Sarabun", color: "404040" },
          paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2 },
        },
        {
          id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 22, bold: true, italics: true, font: "Sarabun" },
          paragraph: { spacing: { before: 140, after: 80 }, outlineLevel: 3 },
        },
      ],
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [
            { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          ],
        },
        {
          reference: "numbers",
          levels: [
            { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          ],
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: 12240, height: 15840 },
            margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
          },
        },
        children,
      },
    ],
  });

  Packer.toBuffer(doc).then((buffer) => {
    fs.writeFileSync(OUT_FILE, buffer);
    console.log(`\nDone -> ${OUT_FILE}`);
  });
}

main();
