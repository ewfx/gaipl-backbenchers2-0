import React, { useState } from "react";
import { Document, Page } from "react-pdf";
import { Card, CardContent, Typography, Button } from "@mui/material";


const PDFIframeViewer = ({ fileUrl }) => {
    const [numPages, setNumPages] = useState(null);
    const [pageNumber, setPageNumber] = useState(1);

    return (
        <Card sx={{ maxWidth: 800, margin: "auto", padding: 2 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    PDF Viewer
                </Typography>
                <Document
                    file={fileUrl}
                    onLoadSuccess={({ numPages }) => setNumPages(numPages)}
                    onLoadError={(error) => console.error("PDF loading error:", error)}
                >
                    <Page pageNumber={pageNumber} />
                </Document>
                <Typography variant="body2" align="center">
                    Page {pageNumber} of {numPages}
                </Typography>
                <div style={{ display: "flex", justifyContent: "center", marginTop: 10 }}>
                    <Button
                        variant="contained"
                        onClick={() => setPageNumber((prev) => Math.max(prev - 1, 1))}
                        disabled={pageNumber === 1}
                        sx={{ marginRight: 1 }}
                    >
                        Prev
                    </Button>
                    <Button
                        variant="contained"
                        onClick={() => setPageNumber((prev) => Math.min(prev + 1, numPages))}
                        disabled={pageNumber === numPages}
                    >
                        Next
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
};

export default PDFIframeViewer;
