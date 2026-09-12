package main

import (
	"testing"
)

func TestParseImageCoordinates(t *testing.T) {
	tests := []struct {
		name             string
		annotations      map[string]string
		wantDistribution string
		wantPgMajor      int
		wantErr          bool
	}{
		{
			name: "valid annotations",
			annotations: map[string]string{
				AnnotationImageBaseOS:      "bookworm",
				AnnotationImageBasePgMajor: "17",
			},
			wantDistribution: "bookworm",
			wantPgMajor:      17,
		},
		{
			name:        "nil annotations",
			annotations: nil,
			wantErr:     true,
		},
		{
			name: "missing distribution",
			annotations: map[string]string{
				AnnotationImageBasePgMajor: "18",
			},
			wantErr: true,
		},
		{
			name: "empty distribution",
			annotations: map[string]string{
				AnnotationImageBaseOS:      "",
				AnnotationImageBasePgMajor: "18",
			},
			wantErr: true,
		},
		{
			name: "missing pgmajor",
			annotations: map[string]string{
				AnnotationImageBaseOS: "trixie",
			},
			wantErr: true,
		},
		{
			name: "non-numeric pgmajor",
			annotations: map[string]string{
				AnnotationImageBaseOS:      "trixie",
				AnnotationImageBasePgMajor: "trixie",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			distribution, pgMajor, err := parseImageCoordinates(tt.annotations)
			if tt.wantErr {
				if err == nil {
					t.Fatal("expected an error, got nil")
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if distribution != tt.wantDistribution {
				t.Errorf("distribution: got %q, want %q", distribution, tt.wantDistribution)
			}
			if pgMajor != tt.wantPgMajor {
				t.Errorf("pgMajor: got %d, want %d", pgMajor, tt.wantPgMajor)
			}
		})
	}
}

func TestExtractExtensionVersion(t *testing.T) {
	tests := []struct {
		name        string
		packageName string
		want        string
		wantErr     bool
	}{
		{
			name:        "standard Debian package version",
			packageName: "1.7.0-1.pgdg12+1",
			want:        "1.7.0",
		},
		{
			name:        "Debian package version with epoch",
			packageName: "1:8.4.8.6-1.pgdg12+1",
			want:        "1-8.4.8.6",
		},
		{
			name:        "package version without an extension version",
			packageName: "1:pkg-1",
			wantErr:     true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			versions := versionMap{
				"bookworm": {
					"18": {Package: tt.packageName},
				},
			}

			got, err := extractExtensionVersion(versions, "bookworm", 18)
			if tt.wantErr {
				if err == nil {
					t.Fatal("expected an error, got nil")
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("version: got %q, want %q", got, tt.want)
			}
		})
	}
}
