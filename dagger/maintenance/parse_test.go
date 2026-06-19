package main

import (
	"slices"
	"testing"
)

func TestBuildMatrixFromMetadata(t *testing.T) {
	tests := []struct {
		name     string
		versions versionMap
		want     []buildCombo
	}{
		{
			name: "two distros, one major",
			versions: versionMap{
				"trixie":   {"18": {Package: "x"}},
				"bookworm": {"18": {Package: "x"}},
			},
			want: []buildCombo{
				{Distribution: "bookworm", MajorVersion: "18"},
				{Distribution: "trixie", MajorVersion: "18"},
			},
		},
		{
			name: "single distro",
			versions: versionMap{
				"trixie": {"18": {Package: "x"}},
			},
			want: []buildCombo{
				{Distribution: "trixie", MajorVersion: "18"},
			},
		},
		{
			// Each distribution declares its own set of PG majors:
			// bookworm builds 17 and 18, trixie builds only 18.
			// There must be no trixie/17 combo.
			name: "each distro declares its own majors",
			versions: versionMap{
				"bookworm": {"17": {Package: "x"}, "18": {Package: "x"}},
				"trixie":   {"18": {Package: "x"}},
			},
			want: []buildCombo{
				{Distribution: "bookworm", MajorVersion: "17"},
				{Distribution: "bookworm", MajorVersion: "18"},
				{Distribution: "trixie", MajorVersion: "18"},
			},
		},
		{
			name:     "empty versions",
			versions: versionMap{},
			want:     nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			matrix := buildMatrixFromMetadata(&extensionMetadata{Versions: tt.versions})

			if !slices.Equal(matrix.Combinations, tt.want) {
				t.Errorf("Combinations: got %v, want %v", matrix.Combinations, tt.want)
			}
		})
	}
}

func TestBuildMatrix(t *testing.T) {
	matrix := buildMatrixFromMetadata(&extensionMetadata{Versions: versionMap{
		"bookworm": {"18": {Package: "x"}, "19": {Package: "x"}},
		"trixie":   {"18": {Package: "x"}},
	}})

	t.Run("contains", func(t *testing.T) {
		cases := []struct {
			distro string
			major  string
			want   bool
		}{
			{"bookworm", "18", true},
			{"bookworm", "19", true},
			{"trixie", "18", true},
			{"trixie", "19", false},   // trixie does not declare 19
			{"bullseye", "18", false}, // bullseye is not present
		}
		for _, c := range cases {
			if got := matrix.contains(c.distro, c.major); got != c.want {
				t.Errorf("contains(%q, %q) = %v, want %v", c.distro, c.major, got, c.want)
			}
		}
	})

	t.Run("hasDistribution", func(t *testing.T) {
		if !matrix.hasDistribution("trixie") {
			t.Error("hasDistribution(trixie) = false, want true")
		}
		if matrix.hasDistribution("bullseye") {
			t.Error("hasDistribution(bullseye) = true, want false")
		}
	})
}
