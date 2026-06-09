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
