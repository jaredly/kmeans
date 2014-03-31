
use std::io;
use std::os;
use std::num::strconv::{from_str_common, ExpNone};

fn strtofloat(x: &str) -> Option<f64> {
  from_str_common(x, 10, false, true, false, ExpNone, false, false)
}

enum Best {
  NoBest,
  Best(f64, uint, uint)
}

fn dist(one: &[uint], two: &[uint], mx: &~[~[f64]]) -> f64 {
  1.0
}

fn step(clusters: &mut ~[~[uint]], mx: &~[~[f64]]) {
  let mut best = NoBest;
  let len = clusters.len();
  for i in range(0, len) {
    for j in range(i + 1, len) {
      let d = dist(clusters[i], clusters[j], mx);
      match best {
        NoBest => best = Best(d, i, j),
        Best(bdist, _, _) if bdist > d => best = Best(d, i, j),
        _ => {}
      }
    }
  }
  match best {
    Best(_, i, j) => {
      println!("merging {} and {}", i, j);
      clusters.remove(j).map(|x| x.map(|y| clusters[j].push(*y)));
      println!("now {} ", clusters.len());
    },
    _ => {}
  }
}

fn main() {
  let mut mx: ~[~[f64]] = ~[];
  for line in io::stdin().lines() {
    let items = line.unwrap().split(';').filter_map(strtofloat).collect();
    // println!("{}", items);
    mx.push(items);
  }
  let mut clusters: ~[~[uint]] = ~[];
  for i in range(0, mx.len()) {
    clusters.push(~[i]);
  }
  step(&mut clusters, &mx);

  println!("Got {} lines", mx.len());
}

